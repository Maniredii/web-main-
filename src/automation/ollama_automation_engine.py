"""
🧠 Ollama-Powered Automation Engine
Intelligent automation system that uses Ollama for dynamic decision making
"""

import asyncio
import json
import logging
import os
import requests
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AutomationStrategy(Enum):
    """Automation strategies for different scenarios"""
    CONSERVATIVE = "conservative"  # Safe, traditional approach
    ADAPTIVE = "adaptive"         # AI-guided with fallbacks
    AGGRESSIVE = "aggressive"     # Full AI decision making


@dataclass
class AutomationContext:
    """Context for automation decisions"""
    task_type: str
    current_url: str
    page_title: str
    page_content: str
    previous_actions: List[str]
    error_history: List[str]
    user_preferences: Dict[str, Any]


@dataclass
class AutomationDecision:
    """AI-generated automation decision"""
    action_type: str
    target_element: Optional[str]
    input_value: Optional[str]
    reasoning: str
    confidence: float
    fallback_actions: List[str]


class OllamaAutomationEngine:
    """Intelligent automation engine powered by Ollama"""
    
    def __init__(self, 
                 model: str = "qwen2.5:7b",
                 base_url: str = "http://localhost:11434",
                 strategy: AutomationStrategy = AutomationStrategy.ADAPTIVE):
        self.model = model
        self.base_url = base_url
        self.strategy = strategy
        self.available = self._check_availability()
        self.context_history: List[AutomationContext] = []
        
    def _check_availability(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                if self.model in models:
                    logger.info(f"✅ Ollama automation engine ready with {self.model}")
                    return True
                else:
                    logger.warning(f"⚠️ Model {self.model} not found. Available: {models}")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Ollama not available: {e}")
            return False
    
    async def query_ollama(self, prompt: str, max_tokens: int = 1024) -> Optional[str]:
        """Query Ollama with a prompt"""
        if not self.available:
            return None
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.1,
                        'num_predict': max_tokens
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('response', '').strip()
            return None
        except Exception as e:
            logger.error(f"Ollama query failed: {e}")
            return None
    
    async def analyze_automation_context(self, context: AutomationContext) -> AutomationDecision:
        """Analyze context and generate automation decision"""
        if not self.available:
            return self._fallback_decision(context)
        
        prompt = self._build_analysis_prompt(context)
        response = await self.query_ollama(prompt, max_tokens=512)
        
        if response:
            try:
                decision_data = json.loads(response)
                return AutomationDecision(
                    action_type=decision_data.get('action_type', 'wait'),
                    target_element=decision_data.get('target_element'),
                    input_value=decision_data.get('input_value'),
                    reasoning=decision_data.get('reasoning', 'AI analysis'),
                    confidence=float(decision_data.get('confidence', 0.5)),
                    fallback_actions=decision_data.get('fallback_actions', [])
                )
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"Failed to parse Ollama decision: {e}")
        
        return self._fallback_decision(context)
    
    def _build_analysis_prompt(self, context: AutomationContext) -> str:
        """Build analysis prompt for Ollama"""
        return f"""
You are an intelligent web automation assistant. Analyze the current context and suggest the best next action.

Task Type: {context.task_type}
Current URL: {context.current_url}
Page Title: {context.page_title}
Page Content (first 500 chars): {context.page_content[:500]}
Previous Actions: {', '.join(context.previous_actions[-5:])}
Recent Errors: {', '.join(context.error_history[-3:])}

Strategy: {self.strategy.value}

Based on this context, suggest the next automation action. Consider:
1. The current page state and content
2. The task objective
3. Previous actions and any errors
4. Best practices for web automation

Respond with ONLY a JSON object:
{{
    "action_type": "click|type|scroll|navigate|wait|submit",
    "target_element": "CSS selector or description of element",
    "input_value": "text to input (if applicable)",
    "reasoning": "brief explanation of why this action",
    "confidence": 0.8,
    "fallback_actions": ["alternative action if primary fails"]
}}
"""
    
    def _fallback_decision(self, context: AutomationContext) -> AutomationDecision:
        """Generate fallback decision when Ollama is unavailable"""
        # Simple rule-based fallback logic
        if "login" in context.current_url.lower():
            return AutomationDecision(
                action_type="type",
                target_element="input[type='email'], input[name='email']",
                input_value=None,
                reasoning="Detected login page, suggest email input",
                confidence=0.6,
                fallback_actions=["wait", "scroll"]
            )
        elif "job" in context.current_url.lower():
            return AutomationDecision(
                action_type="click",
                target_element="button[contains(text(), 'Apply')], .apply-button",
                input_value=None,
                reasoning="Detected job page, suggest apply button",
                confidence=0.7,
                fallback_actions=["scroll", "wait"]
            )
        else:
            return AutomationDecision(
                action_type="wait",
                target_element=None,
                input_value=None,
                reasoning="Unknown page context, waiting for manual guidance",
                confidence=0.3,
                fallback_actions=["scroll", "navigate_back"]
            )
    
    async def generate_form_data(self, form_fields: List[Dict[str, str]], 
                                user_profile: Dict[str, Any]) -> Dict[str, str]:
        """Generate intelligent form data using Ollama"""
        if not self.available:
            return self._fallback_form_data(form_fields, user_profile)
        
        prompt = f"""
Generate appropriate form field values based on the user profile and field requirements.

User Profile: {json.dumps(user_profile, indent=2)}

Form Fields:
{json.dumps(form_fields, indent=2)}

For each field, provide an appropriate value based on:
1. Field name/label/type
2. User profile information
3. Professional standards
4. Common form patterns

Respond with ONLY a JSON object mapping field names to values:
{{
    "field_name": "appropriate_value",
    ...
}}
"""
        
        response = await self.query_ollama(prompt, max_tokens=512)
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                logger.warning("Failed to parse form data from Ollama")
        
        return self._fallback_form_data(form_fields, user_profile)
    
    def _fallback_form_data(self, form_fields: List[Dict[str, str]], 
                           user_profile: Dict[str, Any]) -> Dict[str, str]:
        """Generate fallback form data without AI"""
        form_data = {}
        
        for field in form_fields:
            field_name = field.get('name', '').lower()
            field_label = field.get('label', '').lower()
            
            # Simple mapping logic
            if any(term in field_name or term in field_label for term in ['email', 'mail']):
                form_data[field['name']] = user_profile.get('email', '')
            elif any(term in field_name or term in field_label for term in ['first', 'fname']):
                form_data[field['name']] = user_profile.get('first_name', '')
            elif any(term in field_name or term in field_label for term in ['last', 'lname']):
                form_data[field['name']] = user_profile.get('last_name', '')
            elif any(term in field_name or term in field_label for term in ['phone', 'tel']):
                form_data[field['name']] = user_profile.get('phone', '')
            else:
                form_data[field['name']] = ''
        
        return form_data
    
    def add_context(self, context: AutomationContext):
        """Add context to history for learning"""
        self.context_history.append(context)
        # Keep only last 50 contexts to manage memory
        if len(self.context_history) > 50:
            self.context_history = self.context_history[-50:]
    
    async def learn_from_feedback(self, context: AutomationContext, 
                                 decision: AutomationDecision, 
                                 success: bool, 
                                 feedback: str = ""):
        """Learn from automation results (future enhancement)"""
        # This could be enhanced to fine-tune the model or adjust prompts
        # based on success/failure patterns
        logger.info(f"Automation feedback: {success} - {feedback}")
