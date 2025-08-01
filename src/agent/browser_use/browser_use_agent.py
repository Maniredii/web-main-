from __future__ import annotations

import asyncio
import logging
import os
import requests
import json
from typing import Optional, Dict, Any

# from lmnr.sdk.decorators import observe
from browser_use.agent.gif import create_history_gif
from browser_use.agent.service import Agent, AgentHookFunc
from browser_use.agent.views import (
    ActionResult,
    AgentHistory,
    AgentHistoryList,
    AgentStepInfo,
    ToolCallingMethod,
)
from browser_use.browser.views import BrowserStateHistory
from browser_use.utils import time_execution_async
from dotenv import load_dotenv
from browser_use.agent.message_manager.utils import is_model_without_tool_support

load_dotenv()
logger = logging.getLogger(__name__)

SKIP_LLM_API_KEY_VERIFICATION = (
        os.environ.get("SKIP_LLM_API_KEY_VERIFICATION", "false").lower()[0] in "ty1"
)


class BrowserUseAgent(Agent):
    def __init__(self, *args, **kwargs):
        """Initialize the agent with Ollama integration"""
        super().__init__(*args, **kwargs)
        self.ollama_config = self._setup_ollama_config()
        self.ollama_available = self._check_ollama_availability()

    def _setup_ollama_config(self) -> Dict[str, Any]:
        """Setup Ollama configuration"""
        return {
            'base_url': os.getenv('OLLAMA_ENDPOINT', 'http://localhost:11434'),
            'model': os.getenv('OLLAMA_MODEL', 'qwen2.5:7b'),
            'temperature': float(os.getenv('OLLAMA_TEMPERATURE', '0.1')),
            'max_tokens': int(os.getenv('OLLAMA_MAX_TOKENS', '1024'))
        }

    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is available and responsive"""
        try:
            response = requests.get(f"{self.ollama_config['base_url']}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                if self.ollama_config['model'] in available_models:
                    logger.info(f"✅ Ollama available with model: {self.ollama_config['model']}")
                    return True
                else:
                    logger.warning(f"⚠️ Ollama model {self.ollama_config['model']} not found. Available: {available_models}")
                    return False
            return False
        except Exception as e:
            logger.warning(f"⚠️ Ollama not available: {e}")
            return False

    async def query_ollama(self, prompt: str, context: Optional[str] = None) -> Optional[str]:
        """Query Ollama for intelligent responses"""
        if not self.ollama_available:
            return None

        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt

            response = requests.post(
                f"{self.ollama_config['base_url']}/api/generate",
                json={
                    'model': self.ollama_config['model'],
                    'prompt': full_prompt,
                    'stream': False,
                    'options': {
                        'temperature': self.ollama_config['temperature'],
                        'num_predict': self.ollama_config['max_tokens']
                    }
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Ollama query error: {e}")
            return None

    async def analyze_page_with_ollama(self, page_content: str, task_context: str) -> Optional[Dict[str, Any]]:
        """Use Ollama to analyze page content and suggest next actions"""
        if not self.ollama_available:
            return None

        prompt = f"""
        Analyze this web page content and suggest the best next action for the given task.

        Task: {task_context}

        Page Content (first 1000 chars): {page_content[:1000]}

        Please respond with a JSON object containing:
        - "action": suggested action type (click, type, scroll, navigate, etc.)
        - "element": description of element to interact with
        - "reasoning": why this action is recommended
        - "confidence": confidence level (0-1)

        Respond with only valid JSON, no additional text.
        """

        response = await self.query_ollama(prompt)
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                logger.warning("Failed to parse Ollama response as JSON")
                return None
        return None

    def _set_tool_calling_method(self) -> ToolCallingMethod | None:
        tool_calling_method = self.settings.tool_calling_method
        if tool_calling_method == 'auto':
            if is_model_without_tool_support(self.model_name):
                return 'raw'
            elif self.chat_model_library == 'ChatGoogleGenerativeAI':
                return None
            elif self.chat_model_library == 'ChatOpenAI':
                return 'function_calling'
            elif self.chat_model_library == 'AzureChatOpenAI':
                return 'function_calling'
            else:
                return None
        else:
            return tool_calling_method

    @time_execution_async("--run (agent)")
    async def run(
            self, max_steps: int = 100, on_step_start: AgentHookFunc | None = None,
            on_step_end: AgentHookFunc | None = None
    ) -> AgentHistoryList:
        """Execute the task with maximum number of steps"""

        loop = asyncio.get_event_loop()

        # Set up the Ctrl+C signal handler with callbacks specific to this agent
        from browser_use.utils import SignalHandler

        signal_handler = SignalHandler(
            loop=loop,
            pause_callback=self.pause,
            resume_callback=self.resume,
            custom_exit_callback=None,  # No special cleanup needed on forced exit
            exit_on_second_int=True,
        )
        signal_handler.register()

        try:
            self._log_agent_run()

            # Execute initial actions if provided
            if self.initial_actions:
                result = await self.multi_act(self.initial_actions, check_for_new_elements=False)
                self.state.last_result = result

            for step in range(max_steps):
                # Check if waiting for user input after Ctrl+C
                if self.state.paused:
                    signal_handler.wait_for_resume()
                    signal_handler.reset()

                # Check if we should stop due to too many failures
                if self.state.consecutive_failures >= self.settings.max_failures:
                    logger.error(f'❌ Stopping due to {self.settings.max_failures} consecutive failures')
                    break

                # Check control flags before each step
                if self.state.stopped:
                    logger.info('Agent stopped')
                    break

                while self.state.paused:
                    await asyncio.sleep(0.2)  # Small delay to prevent CPU spinning
                    if self.state.stopped:  # Allow stopping while paused
                        break

                if on_step_start is not None:
                    await on_step_start(self)

                step_info = AgentStepInfo(step_number=step, max_steps=max_steps)
                await self.step(step_info)

                if on_step_end is not None:
                    await on_step_end(self)

                if self.state.history.is_done():
                    if self.settings.validate_output and step < max_steps - 1:
                        if not await self._validate_output():
                            continue

                    await self.log_completion()
                    break
            else:
                error_message = 'Failed to complete task in maximum steps'

                self.state.history.history.append(
                    AgentHistory(
                        model_output=None,
                        result=[ActionResult(error=error_message, include_in_memory=True)],
                        state=BrowserStateHistory(
                            url='',
                            title='',
                            tabs=[],
                            interacted_element=[],
                            screenshot=None,
                        ),
                        metadata=None,
                    )
                )

                logger.info(f'❌ {error_message}')

            return self.state.history

        except KeyboardInterrupt:
            # Already handled by our signal handler, but catch any direct KeyboardInterrupt as well
            logger.info('Got KeyboardInterrupt during execution, returning current history')
            return self.state.history

        finally:
            # Unregister signal handlers before cleanup
            signal_handler.unregister()

            if self.settings.save_playwright_script_path:
                logger.info(
                    f'Agent run finished. Attempting to save Playwright script to: {self.settings.save_playwright_script_path}'
                )
                try:
                    # Extract sensitive data keys if sensitive_data is provided
                    keys = list(self.sensitive_data.keys()) if self.sensitive_data else None
                    # Pass browser and context config to the saving method
                    self.state.history.save_as_playwright_script(
                        self.settings.save_playwright_script_path,
                        sensitive_data_keys=keys,
                        browser_config=self.browser.config,
                        context_config=self.browser_context.config,
                    )
                except Exception as script_gen_err:
                    # Log any error during script generation/saving
                    logger.error(f'Failed to save Playwright script: {script_gen_err}', exc_info=True)

            await self.close()

            if self.settings.generate_gif:
                output_path: str = 'agent_history.gif'
                if isinstance(self.settings.generate_gif, str):
                    output_path = self.settings.generate_gif

                create_history_gif(task=self.task, history=self.state.history, output_path=output_path)
