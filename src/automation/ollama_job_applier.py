"""
🚀 Ollama-Enhanced Job Application Automation
Intelligent job application system with AI-powered decision making
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from browser_use.browser.context import BrowserContext
from browser_use.agent.service import Agent

from .ollama_automation_engine import OllamaAutomationEngine, AutomationContext, AutomationStrategy

logger = logging.getLogger(__name__)


@dataclass
class JobListing:
    """Job listing information"""
    title: str
    company: str
    location: str
    description: str
    url: str
    salary_range: Optional[str] = None
    requirements: List[str] = None
    benefits: List[str] = None


@dataclass
class ApplicationResult:
    """Result of job application attempt"""
    job: JobListing
    success: bool
    reason: str
    actions_taken: List[str]
    time_taken: float
    ai_confidence: float


class OllamaJobApplier:
    """Intelligent job application automation with Ollama"""
    
    def __init__(self, 
                 user_profile: Dict[str, Any],
                 automation_engine: Optional[OllamaAutomationEngine] = None,
                 strategy: AutomationStrategy = AutomationStrategy.ADAPTIVE):
        self.user_profile = user_profile
        self.automation_engine = automation_engine or OllamaAutomationEngine(strategy=strategy)
        self.applications_sent = 0
        self.application_history: List[ApplicationResult] = []
        
    async def analyze_job_compatibility(self, job: JobListing) -> Dict[str, Any]:
        """Use Ollama to analyze job compatibility with user profile"""
        if not self.automation_engine.available:
            return self._fallback_job_analysis(job)
        
        prompt = f"""
        Analyze this job opportunity for compatibility with the candidate profile.
        
        Job Details:
        - Title: {job.title}
        - Company: {job.company}
        - Location: {job.location}
        - Description: {job.description[:1000]}
        
        Candidate Profile:
        - Skills: {self.user_profile.get('skills', [])}
        - Experience: {self.user_profile.get('experience_years', 0)} years
        - Education: {self.user_profile.get('education', '')}
        - Preferences: {self.user_profile.get('job_preferences', {})}
        
        Analyze compatibility considering:
        1. Skill match percentage
        2. Experience level fit
        3. Location preferences
        4. Career growth potential
        5. Company culture fit
        
        Respond with ONLY a JSON object:
        {{
            "compatibility_score": 0.85,
            "should_apply": true,
            "reasoning": "Strong skill match with Python and ML experience",
            "skill_matches": ["Python", "Machine Learning"],
            "skill_gaps": ["Kubernetes"],
            "salary_expectation_met": true,
            "growth_potential": "high"
        }}
        """
        
        response = await self.automation_engine.query_ollama(prompt, max_tokens=512)
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                logger.warning("Failed to parse job analysis from Ollama")
        
        return self._fallback_job_analysis(job)
    
    def _fallback_job_analysis(self, job: JobListing) -> Dict[str, Any]:
        """Fallback job analysis without AI"""
        user_skills = set(skill.lower() for skill in self.user_profile.get('skills', []))
        job_text = f"{job.title} {job.description}".lower()
        
        # Simple keyword matching
        skill_matches = [skill for skill in user_skills if skill in job_text]
        compatibility_score = min(len(skill_matches) / max(len(user_skills), 1), 1.0)
        
        return {
            "compatibility_score": compatibility_score,
            "should_apply": compatibility_score > 0.3,
            "reasoning": f"Keyword match analysis: {len(skill_matches)} skills matched",
            "skill_matches": skill_matches,
            "skill_gaps": [],
            "salary_expectation_met": True,
            "growth_potential": "unknown"
        }
    
    async def generate_cover_letter(self, job: JobListing) -> str:
        """Generate personalized cover letter using Ollama"""
        if not self.automation_engine.available:
            return self._fallback_cover_letter(job)
        
        prompt = f"""
        Write a professional, personalized cover letter for this job application.
        
        Job Details:
        - Position: {job.title}
        - Company: {job.company}
        - Key Requirements: {job.description[:500]}
        
        Candidate Information:
        - Name: {self.user_profile.get('full_name', 'Candidate')}
        - Experience: {self.user_profile.get('experience_years', 0)} years
        - Skills: {', '.join(self.user_profile.get('skills', [])[:5])}
        - Current Role: {self.user_profile.get('current_position', '')}
        
        Requirements:
        - Professional tone
        - 3-4 paragraphs maximum
        - Highlight relevant experience
        - Show enthusiasm for the role
        - Mention specific skills that match
        - No generic phrases
        
        Write only the cover letter content, no subject line or formatting.
        """
        
        response = await self.automation_engine.query_ollama(prompt, max_tokens=400)
        if response:
            return response.strip()
        
        return self._fallback_cover_letter(job)
    
    def _fallback_cover_letter(self, job: JobListing) -> str:
        """Generate fallback cover letter without AI"""
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job.title} position at {job.company}. With {self.user_profile.get('experience_years', 0)} years of experience in software development and expertise in {', '.join(self.user_profile.get('skills', [])[:3])}, I am confident I would be a valuable addition to your team.

My background in {self.user_profile.get('current_position', 'software development')} has equipped me with the technical skills and problem-solving abilities that align well with your requirements. I am particularly excited about the opportunity to contribute to {job.company}'s mission and grow my career in this role.

I would welcome the opportunity to discuss how my experience and enthusiasm can benefit your team. Thank you for considering my application.

Best regards,
{self.user_profile.get('full_name', 'Candidate')}"""
    
    async def apply_to_job(self, job: JobListing, browser_context: BrowserContext) -> ApplicationResult:
        """Apply to a single job with AI assistance"""
        start_time = asyncio.get_event_loop().time()
        actions_taken = []
        
        try:
            # Step 1: Analyze job compatibility
            analysis = await self.analyze_job_compatibility(job)
            actions_taken.append(f"Analyzed job compatibility: {analysis['compatibility_score']:.2f}")
            
            if not analysis['should_apply']:
                return ApplicationResult(
                    job=job,
                    success=False,
                    reason=f"Job not suitable: {analysis['reasoning']}",
                    actions_taken=actions_taken,
                    time_taken=asyncio.get_event_loop().time() - start_time,
                    ai_confidence=analysis['compatibility_score']
                )
            
            # Step 2: Navigate to job page
            await browser_context.goto(job.url)
            actions_taken.append("Navigated to job page")
            
            # Step 3: Find and click apply button
            apply_success = await self._find_and_click_apply_button(browser_context)
            if not apply_success:
                return ApplicationResult(
                    job=job,
                    success=False,
                    reason="Could not find apply button",
                    actions_taken=actions_taken,
                    time_taken=asyncio.get_event_loop().time() - start_time,
                    ai_confidence=0.0
                )
            
            actions_taken.append("Clicked apply button")
            
            # Step 4: Fill application form with AI assistance
            form_success = await self._fill_application_form(browser_context, job)
            if not form_success:
                return ApplicationResult(
                    job=job,
                    success=False,
                    reason="Failed to fill application form",
                    actions_taken=actions_taken,
                    time_taken=asyncio.get_event_loop().time() - start_time,
                    ai_confidence=0.5
                )
            
            actions_taken.append("Filled application form")
            
            # Step 5: Submit application
            submit_success = await self._submit_application(browser_context)
            if submit_success:
                self.applications_sent += 1
                actions_taken.append("Successfully submitted application")
                
                return ApplicationResult(
                    job=job,
                    success=True,
                    reason="Application submitted successfully",
                    actions_taken=actions_taken,
                    time_taken=asyncio.get_event_loop().time() - start_time,
                    ai_confidence=analysis['compatibility_score']
                )
            else:
                return ApplicationResult(
                    job=job,
                    success=False,
                    reason="Failed to submit application",
                    actions_taken=actions_taken,
                    time_taken=asyncio.get_event_loop().time() - start_time,
                    ai_confidence=0.3
                )
                
        except Exception as e:
            logger.error(f"Error applying to job {job.title}: {e}")
            return ApplicationResult(
                job=job,
                success=False,
                reason=f"Exception occurred: {str(e)}",
                actions_taken=actions_taken,
                time_taken=asyncio.get_event_loop().time() - start_time,
                ai_confidence=0.0
            )
    
    async def _find_and_click_apply_button(self, browser_context: BrowserContext) -> bool:
        """Find and click apply button using AI assistance"""
        try:
            # Get page content for AI analysis
            page_content = await browser_context.get_page_content()
            
            # Use AI to identify the best apply button
            context = AutomationContext(
                task_type="find_apply_button",
                current_url=browser_context.current_url,
                page_title=await browser_context.get_page_title(),
                page_content=page_content,
                previous_actions=[],
                error_history=[],
                user_preferences=self.user_profile
            )
            
            decision = await self.automation_engine.analyze_automation_context(context)
            
            if decision.target_element:
                # Try to click the AI-suggested element
                elements = await browser_context.find_elements(decision.target_element)
                if elements:
                    await elements[0].click()
                    return True
            
            # Fallback to common selectors
            apply_selectors = [
                "button[aria-label*='Easy Apply']",
                "button:contains('Easy Apply')",
                "button:contains('Apply')",
                ".apply-button",
                "[data-test*='apply']"
            ]
            
            for selector in apply_selectors:
                try:
                    elements = await browser_context.find_elements(selector)
                    if elements:
                        await elements[0].click()
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error finding apply button: {e}")
            return False
    
    async def _fill_application_form(self, browser_context: BrowserContext, job: JobListing) -> bool:
        """Fill application form with AI assistance"""
        try:
            # Find all form fields
            form_fields = await self._extract_form_fields(browser_context)
            
            if not form_fields:
                return True  # No form to fill
            
            # Generate form data using AI
            form_data = await self.automation_engine.generate_form_data(form_fields, self.user_profile)
            
            # Fill each field
            for field in form_fields:
                field_name = field.get('name', '')
                if field_name in form_data:
                    try:
                        element = await browser_context.find_element(f"[name='{field_name}']")
                        if element:
                            await element.fill(form_data[field_name])
                    except:
                        continue
            
            return True
            
        except Exception as e:
            logger.error(f"Error filling form: {e}")
            return False
    
    async def _extract_form_fields(self, browser_context: BrowserContext) -> List[Dict[str, str]]:
        """Extract form fields from the page"""
        try:
            # This would need to be implemented based on the specific browser automation library
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error extracting form fields: {e}")
            return []
    
    async def _submit_application(self, browser_context: BrowserContext) -> bool:
        """Submit the application"""
        try:
            submit_selectors = [
                "button[type='submit']",
                "button:contains('Submit')",
                "button:contains('Send Application')",
                ".submit-button"
            ]
            
            for selector in submit_selectors:
                try:
                    elements = await browser_context.find_elements(selector)
                    if elements:
                        await elements[0].click()
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error submitting application: {e}")
            return False
