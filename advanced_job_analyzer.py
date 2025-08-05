#!/usr/bin/env python3
"""
🧠 Advanced Job Analysis Engine
Uses Ollama for comprehensive job evaluation and matching
"""

import json
import logging
import requests
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Types of job analysis"""
    COMPATIBILITY = "compatibility"
    SKILL_MATCH = "skill_match"
    SALARY_ANALYSIS = "salary_analysis"
    COMPANY_CULTURE = "company_culture"
    SUCCESS_PROBABILITY = "success_probability"
    COVER_LETTER = "cover_letter"

@dataclass
class JobAnalysis:
    """Comprehensive job analysis result"""
    job_title: str
    company: str
    overall_score: float
    compatibility_score: float
    skill_match_score: float
    salary_score: float
    culture_score: float
    success_probability: float
    should_apply: bool
    reasoning: str
    skill_gaps: List[str]
    skill_matches: List[str]
    salary_insights: Dict[str, Any]
    company_insights: Dict[str, Any]
    cover_letter_suggestions: List[str]
    application_strategy: str

class AdvancedJobAnalyzer:
    """Advanced job analysis using Ollama"""
    
    def __init__(self, ollama_endpoint: str = "http://localhost:11434", model: str = "qwen2.5:7b"):
        self.ollama_endpoint = ollama_endpoint
        self.model = model
        self.available = self._check_ollama_availability()
        
    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.ollama_endpoint}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    def query_ollama(self, prompt: str, max_tokens: int = 1024) -> Optional[str]:
        """Query Ollama with a prompt"""
        if not self.available:
            return None
            
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                f"{self.ollama_endpoint}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                logger.error(f"Ollama query failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Ollama query error: {e}")
            return None
    
    def analyze_job_compatibility(self, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> JobAnalysis:
        """Comprehensive job analysis"""
        
        # Create analysis prompt
        analysis_prompt = self._create_analysis_prompt(job_data, user_profile)
        
        # Get AI analysis
        ai_response = self.query_ollama(analysis_prompt)
        
        if ai_response:
            try:
                # Parse AI response
                analysis_result = self._parse_ai_response(ai_response)
                return self._create_job_analysis(job_data, analysis_result)
            except Exception as e:
                logger.error(f"Failed to parse AI response: {e}")
                return self._fallback_analysis(job_data, user_profile)
        else:
            return self._fallback_analysis(job_data, user_profile)
    
    def _create_analysis_prompt(self, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """Create comprehensive analysis prompt"""
        
        prompt = f"""
        Analyze this job posting for compatibility with the candidate profile.
        
        JOB DETAILS:
        Title: {job_data.get('title', '')}
        Company: {job_data.get('company', '')}
        Location: {job_data.get('location', '')}
        Description: {job_data.get('description', '')[:1000]}
        Requirements: {job_data.get('requirements', '')}
        Salary: {job_data.get('salary', '')}
        
        CANDIDATE PROFILE:
        Current Title: {user_profile.get('current_title', '')}
        Experience: {user_profile.get('experience_years', 0)} years
        Skills: {', '.join(user_profile.get('skills', []))}
        Education: {user_profile.get('education', '')}
        Desired Salary: {user_profile.get('salary_expectations', {}).get('preferred', 0)}
        Preferred Locations: {', '.join(user_profile.get('preferred_locations', []))}
        
        Please provide a comprehensive analysis in JSON format with the following structure:
        {{
            "overall_score": 0.85,
            "compatibility_score": 0.90,
            "skill_match_score": 0.85,
            "salary_score": 0.80,
            "culture_score": 0.75,
            "success_probability": 0.70,
            "should_apply": true,
            "reasoning": "Strong skill match with Python and React...",
            "skill_gaps": ["AWS", "Docker"],
            "skill_matches": ["Python", "React", "JavaScript"],
            "salary_insights": {{
                "market_average": 85000,
                "salary_range": "80k-90k",
                "negotiation_power": "high"
            }},
            "company_insights": {{
                "growth_potential": "high",
                "culture_fit": "good",
                "stability": "medium"
            }},
            "cover_letter_suggestions": [
                "Highlight Python experience",
                "Mention React projects",
                "Emphasize problem-solving skills"
            ],
            "application_strategy": "Apply immediately with customized resume"
        }}
        
        Focus on:
        1. Skill compatibility and gaps
        2. Salary expectations vs market
        3. Company culture fit
        4. Success probability
        5. Application strategy
        """
        
        return prompt
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured data"""
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            raise
    
    def _create_job_analysis(self, job_data: Dict[str, Any], ai_result: Dict[str, Any]) -> JobAnalysis:
        """Create JobAnalysis object from AI result"""
        
        return JobAnalysis(
            job_title=job_data.get('title', ''),
            company=job_data.get('company', ''),
            overall_score=ai_result.get('overall_score', 0.0),
            compatibility_score=ai_result.get('compatibility_score', 0.0),
            skill_match_score=ai_result.get('skill_match_score', 0.0),
            salary_score=ai_result.get('salary_score', 0.0),
            culture_score=ai_result.get('culture_score', 0.0),
            success_probability=ai_result.get('success_probability', 0.0),
            should_apply=ai_result.get('should_apply', False),
            reasoning=ai_result.get('reasoning', ''),
            skill_gaps=ai_result.get('skill_gaps', []),
            skill_matches=ai_result.get('skill_matches', []),
            salary_insights=ai_result.get('salary_insights', {}),
            company_insights=ai_result.get('company_insights', {}),
            cover_letter_suggestions=ai_result.get('cover_letter_suggestions', []),
            application_strategy=ai_result.get('application_strategy', '')
        )
    
    def _fallback_analysis(self, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> JobAnalysis:
        """Fallback analysis when AI is not available"""
        
        # Simple keyword matching
        user_skills = set(skill.lower() for skill in user_profile.get('skills', []))
        job_text = f"{job_data.get('title', '')} {job_data.get('description', '')}".lower()
        
        skill_matches = [skill for skill in user_skills if skill in job_text]
        skill_gaps = list(user_skills - set(skill_matches))
        
        compatibility_score = min(len(skill_matches) / max(len(user_skills), 1), 1.0)
        
        return JobAnalysis(
            job_title=job_data.get('title', ''),
            company=job_data.get('company', ''),
            overall_score=compatibility_score,
            compatibility_score=compatibility_score,
            skill_match_score=compatibility_score,
            salary_score=0.5,
            culture_score=0.5,
            success_probability=compatibility_score * 0.8,
            should_apply=compatibility_score > 0.3,
            reasoning=f"Keyword analysis: {len(skill_matches)} skills matched",
            skill_gaps=skill_gaps,
            skill_matches=skill_matches,
            salary_insights={},
            company_insights={},
            cover_letter_suggestions=[],
            application_strategy="Apply if interested"
        )
    
    def generate_cover_letter(self, job_data: Dict[str, Any], user_profile: Dict[str, Any], analysis: JobAnalysis) -> str:
        """Generate personalized cover letter using Ollama"""
        
        prompt = f"""
        Generate a personalized cover letter for this job application.
        
        JOB: {job_data.get('title')} at {job_data.get('company')}
        COMPANY: {job_data.get('company')}
        LOCATION: {job_data.get('location')}
        
        CANDIDATE:
        Name: {user_profile.get('name', '')}
        Current Role: {user_profile.get('current_title', '')}
        Experience: {user_profile.get('experience_years', 0)} years
        Key Skills: {', '.join(analysis.skill_matches)}
        
        ANALYSIS INSIGHTS:
        - Skill Matches: {', '.join(analysis.skill_matches)}
        - Key Strengths: {analysis.reasoning}
        - Application Strategy: {analysis.application_strategy}
        
        COVER LETTER SUGGESTIONS:
        {chr(10).join(f"- {suggestion}" for suggestion in analysis.cover_letter_suggestions)}
        
        Generate a compelling, personalized cover letter that:
        1. Shows enthusiasm for the role and company
        2. Highlights relevant skills and experience
        3. Addresses specific job requirements
        4. Demonstrates cultural fit
        5. Includes a clear call to action
        
        Keep it professional, concise (200-300 words), and tailored to this specific opportunity.
        """
        
        response = self.query_ollama(prompt, max_tokens=512)
        return response if response else self._generate_fallback_cover_letter(job_data, user_profile)
    
    def _generate_fallback_cover_letter(self, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """Generate fallback cover letter"""
        
        return f"""
Dear Hiring Manager,

I am excited to apply for the {job_data.get('title')} position at {job_data.get('company')}. With {user_profile.get('experience_years', 0)} years of experience in {user_profile.get('current_title', 'software development')}, I am confident in my ability to contribute effectively to your team.

My background includes expertise in {', '.join(user_profile.get('skills', [])[:3])}, which I believe align well with the requirements for this role. I am particularly drawn to {job_data.get('company')} because of its reputation for innovation and growth.

I would welcome the opportunity to discuss how my skills and experience can benefit {job_data.get('company')} and contribute to your continued success.

Thank you for considering my application.

Best regards,
{user_profile.get('name', '')}
        """.strip()
    
    def analyze_salary_market(self, job_title: str, location: str, experience_years: int) -> Dict[str, Any]:
        """Analyze salary market data using Ollama"""
        
        prompt = f"""
        Analyze the salary market for this position and provide insights.
        
        Position: {job_title}
        Location: {location}
        Experience: {experience_years} years
        
        Provide salary analysis in JSON format:
        {{
            "market_average": 85000,
            "salary_range": "80k-90k",
            "percentile_25": 75000,
            "percentile_75": 95000,
            "negotiation_power": "high/medium/low",
            "market_trend": "increasing/stable/decreasing",
            "location_factor": 1.2,
            "experience_bonus": 5000,
            "recommended_salary": 87000,
            "negotiation_strategy": "Focus on value proposition..."
        }}
        """
        
        response = self.query_ollama(prompt, max_tokens=512)
        
        if response:
            try:
                return json.loads(response)
            except:
                pass
        
        # Fallback salary analysis
        return {
            "market_average": 80000,
            "salary_range": "75k-85k",
            "negotiation_power": "medium",
            "recommended_salary": 82000
        } 