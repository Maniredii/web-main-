"""
Job Description Parser for LinkedIn Automation
Extracts and analyzes job requirements from LinkedIn job postings
"""

import re
import json
import logging
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class JobRequirements:
    """Structured job requirements extracted from job description"""
    # Basic job info
    title: str = ""
    company: str = ""
    location: str = ""
    job_type: str = ""  # Full-time, Part-time, Contract, etc.
    experience_level: str = ""  # Entry, Mid, Senior, etc.
    
    # Technical requirements
    required_skills: List[str] = None
    preferred_skills: List[str] = None
    programming_languages: List[str] = None
    frameworks_tools: List[str] = None
    databases: List[str] = None
    cloud_platforms: List[str] = None
    
    # Experience requirements
    years_experience: Optional[int] = None
    education_requirements: List[str] = None
    certifications: List[str] = None
    
    # Industry-specific keywords
    industry_keywords: List[str] = None
    domain_knowledge: List[str] = None
    
    # Soft skills and qualifications
    soft_skills: List[str] = None
    responsibilities: List[str] = None
    
    # ATS keywords (all important keywords for optimization)
    ats_keywords: List[str] = None
    keyword_frequency: Dict[str, int] = None
    
    # Metadata
    parsed_date: str = ""
    job_url: str = ""
    raw_description: str = ""
    
    def __post_init__(self):
        """Initialize empty lists for None fields"""
        for field_name, field_type in self.__annotations__.items():
            if getattr(self, field_name) is None:
                if hasattr(field_type, '__origin__') and field_type.__origin__ is list:
                    setattr(self, field_name, [])
                elif hasattr(field_type, '__origin__') and field_type.__origin__ is dict:
                    setattr(self, field_name, {})

class JobDescriptionParser:
    """Intelligent job description parser with AI enhancement"""
    
    def __init__(self, ollama_client=None):
        self.ollama_client = ollama_client
        
        # Predefined skill categories for better extraction
        self.skill_patterns = {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
                'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql'
            ],
            'frameworks_tools': [
                'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express',
                'node.js', 'laravel', 'rails', 'asp.net', 'tensorflow', 'pytorch',
                'docker', 'kubernetes', 'jenkins', 'git', 'jira', 'confluence'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
                'oracle', 'sql server', 'sqlite', 'cassandra', 'dynamodb'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean',
                's3', 'ec2', 'lambda', 'cloudformation', 'terraform'
            ],
            'soft_skills': [
                'communication', 'teamwork', 'leadership', 'problem solving',
                'analytical thinking', 'creativity', 'adaptability', 'time management',
                'project management', 'collaboration', 'mentoring', 'agile', 'scrum'
            ]
        }
        
        # Experience level patterns
        self.experience_patterns = {
            'entry': ['entry level', 'junior', '0-2 years', 'new grad', 'graduate'],
            'mid': ['mid level', 'intermediate', '2-5 years', '3-5 years'],
            'senior': ['senior', 'lead', '5+ years', '7+ years', 'expert', 'principal'],
            'executive': ['director', 'manager', 'vp', 'cto', 'ceo', 'head of']
        }
        
        # Education patterns
        self.education_patterns = [
            'bachelor', 'master', 'phd', 'degree', 'computer science', 'engineering',
            'mathematics', 'statistics', 'mba', 'certification'
        ]
    
    def parse_job_description(self, job_text: str, job_url: str = "", 
                            job_title: str = "", company: str = "") -> JobRequirements:
        """
        Parse job description text and extract structured requirements
        
        Args:
            job_text: Raw job description text
            job_url: URL of the job posting
            job_title: Job title if available
            company: Company name if available
            
        Returns:
            JobRequirements object with extracted information
        """
        logger.info(f"Parsing job description for: {job_title} at {company}")
        
        # Clean and normalize text
        cleaned_text = self._clean_text(job_text)
        
        # Initialize requirements object
        requirements = JobRequirements(
            title=job_title,
            company=company,
            job_url=job_url,
            raw_description=job_text,
            parsed_date=datetime.now().isoformat()
        )
        
        # Extract basic information
        requirements.location = self._extract_location(cleaned_text)
        requirements.job_type = self._extract_job_type(cleaned_text)
        requirements.experience_level = self._extract_experience_level(cleaned_text)
        requirements.years_experience = self._extract_years_experience(cleaned_text)
        
        # Extract technical skills
        requirements.programming_languages = self._extract_skills(
            cleaned_text, self.skill_patterns['programming_languages']
        )
        requirements.frameworks_tools = self._extract_skills(
            cleaned_text, self.skill_patterns['frameworks_tools']
        )
        requirements.databases = self._extract_skills(
            cleaned_text, self.skill_patterns['databases']
        )
        requirements.cloud_platforms = self._extract_skills(
            cleaned_text, self.skill_patterns['cloud_platforms']
        )
        requirements.soft_skills = self._extract_skills(
            cleaned_text, self.skill_patterns['soft_skills']
        )
        
        # Extract requirements and preferences
        requirements.required_skills, requirements.preferred_skills = self._extract_skill_requirements(cleaned_text)
        requirements.education_requirements = self._extract_education(cleaned_text)
        requirements.responsibilities = self._extract_responsibilities(cleaned_text)
        
        # Generate ATS keywords
        requirements.ats_keywords = self._generate_ats_keywords(requirements)
        requirements.keyword_frequency = self._calculate_keyword_frequency(cleaned_text, requirements.ats_keywords)
        
        # Use AI enhancement if available
        if self.ollama_client:
            requirements = self._enhance_with_ai(requirements, cleaned_text)
        
        logger.info(f"Extracted {len(requirements.ats_keywords)} ATS keywords")
        return requirements
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize job description text"""
        # Remove HTML tags if present
        text = BeautifulSoup(text, 'html.parser').get_text()
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Convert to lowercase for processing
        return text.lower().strip()
    
    def _extract_location(self, text: str) -> str:
        """Extract job location from text"""
        location_patterns = [
            r'location[:\s]+([^,\n]+)',
            r'based in ([^,\n]+)',
            r'office in ([^,\n]+)',
            r'remote',
            r'hybrid'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip() if match.groups() else match.group(0)
        
        return ""
    
    def _extract_job_type(self, text: str) -> str:
        """Extract job type (full-time, part-time, etc.)"""
        job_types = ['full-time', 'part-time', 'contract', 'temporary', 'internship', 'freelance']
        
        for job_type in job_types:
            if job_type in text:
                return job_type
        
        return ""
    
    def _extract_experience_level(self, text: str) -> str:
        """Extract experience level from text"""
        for level, patterns in self.experience_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    return level
        
        return ""
    
    def _extract_years_experience(self, text: str) -> Optional[int]:
        """Extract years of experience requirement"""
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)-\d+\s*years?',
            r'minimum\s*(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_skills(self, text: str, skill_list: List[str]) -> List[str]:
        """Extract skills from predefined skill list"""
        found_skills = []
        
        for skill in skill_list:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text):
                found_skills.append(skill)
        
        return found_skills
    
    def _extract_skill_requirements(self, text: str) -> Tuple[List[str], List[str]]:
        """Separate required vs preferred skills"""
        required_skills = []
        preferred_skills = []
        
        # Look for required skills sections
        required_patterns = [
            r'required[:\s]+(.*?)(?:preferred|nice|bonus|plus|\n\n)',
            r'must have[:\s]+(.*?)(?:preferred|nice|bonus|plus|\n\n)',
            r'essential[:\s]+(.*?)(?:preferred|nice|bonus|plus|\n\n)'
        ]
        
        # Look for preferred skills sections
        preferred_patterns = [
            r'preferred[:\s]+(.*?)(?:required|must|essential|\n\n)',
            r'nice to have[:\s]+(.*?)(?:required|must|essential|\n\n)',
            r'bonus[:\s]+(.*?)(?:required|must|essential|\n\n)',
            r'plus[:\s]+(.*?)(?:required|must|essential|\n\n)'
        ]
        
        for pattern in required_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                skills_text = match.group(1)
                required_skills.extend(self._extract_skills_from_text(skills_text))
        
        for pattern in preferred_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                skills_text = match.group(1)
                preferred_skills.extend(self._extract_skills_from_text(skills_text))
        
        return required_skills, preferred_skills
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract individual skills from a text block"""
        # Split by common delimiters
        skills = re.split(r'[,;•\n\-\*]', text)
        
        # Clean and filter skills
        cleaned_skills = []
        for skill in skills:
            skill = skill.strip()
            if len(skill) > 2 and len(skill) < 50:  # Reasonable skill length
                cleaned_skills.append(skill)
        
        return cleaned_skills
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education requirements"""
        education_reqs = []
        
        for pattern in self.education_patterns:
            if pattern in text:
                education_reqs.append(pattern)
        
        return education_reqs
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities"""
        responsibility_patterns = [
            r'responsibilities[:\s]+(.*?)(?:requirements|qualifications|\n\n)',
            r'duties[:\s]+(.*?)(?:requirements|qualifications|\n\n)',
            r'you will[:\s]+(.*?)(?:requirements|qualifications|\n\n)'
        ]
        
        responsibilities = []
        for pattern in responsibility_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                resp_text = match.group(1)
                responsibilities.extend(self._extract_skills_from_text(resp_text))
        
        return responsibilities
    
    def _generate_ats_keywords(self, requirements: JobRequirements) -> List[str]:
        """Generate comprehensive ATS keywords from all extracted information"""
        keywords = set()
        
        # Add all technical skills
        keywords.update(requirements.programming_languages)
        keywords.update(requirements.frameworks_tools)
        keywords.update(requirements.databases)
        keywords.update(requirements.cloud_platforms)
        
        # Add required and preferred skills
        keywords.update(requirements.required_skills)
        keywords.update(requirements.preferred_skills)
        
        # Add soft skills
        keywords.update(requirements.soft_skills)
        
        # Add education requirements
        keywords.update(requirements.education_requirements)
        
        # Add job-specific terms
        if requirements.title:
            keywords.add(requirements.title.lower())
        if requirements.experience_level:
            keywords.add(requirements.experience_level)
        
        # Remove empty strings and convert to list
        return [kw for kw in keywords if kw and len(kw.strip()) > 1]
    
    def _calculate_keyword_frequency(self, text: str, keywords: List[str]) -> Dict[str, int]:
        """Calculate frequency of keywords in job description"""
        frequency = {}
        
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            matches = re.findall(pattern, text)
            frequency[keyword] = len(matches)
        
        return frequency
    
    def _enhance_with_ai(self, requirements: JobRequirements, text: str) -> JobRequirements:
        """Use Ollama AI to enhance job requirement extraction"""
        try:
            prompt = f"""
            Analyze this job description and extract additional insights:
            
            Job Description:
            {text[:2000]}...
            
            Please identify:
            1. Any technical skills or tools not already captured
            2. Industry-specific terminology
            3. Hidden requirements or qualifications
            4. Key responsibilities that indicate required experience
            
            Respond in JSON format with these fields:
            - additional_skills: []
            - industry_terms: []
            - hidden_requirements: []
            - key_responsibilities: []
            """
            
            response = self.ollama_client.query(prompt, max_tokens=512)
            if response:
                try:
                    ai_insights = json.loads(response)
                    
                    # Merge AI insights with existing requirements
                    if 'additional_skills' in ai_insights:
                        requirements.ats_keywords.extend(ai_insights['additional_skills'])
                    
                    if 'industry_terms' in ai_insights:
                        requirements.industry_keywords = ai_insights['industry_terms']
                    
                    if 'key_responsibilities' in ai_insights:
                        requirements.responsibilities.extend(ai_insights['key_responsibilities'])
                    
                    logger.info("Enhanced job requirements with AI insights")
                    
                except json.JSONDecodeError:
                    logger.warning("Failed to parse AI response as JSON")
                    
        except Exception as e:
            logger.warning(f"AI enhancement failed: {e}")
        
        return requirements
    
    def save_requirements(self, requirements: JobRequirements, filepath: str):
        """Save job requirements to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(asdict(requirements), f, indent=2)
            logger.info(f"Job requirements saved to: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save requirements: {e}")
    
    def load_requirements(self, filepath: str) -> Optional[JobRequirements]:
        """Load job requirements from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return JobRequirements(**data)
        except Exception as e:
            logger.error(f"Failed to load requirements: {e}")
            return None

# Example usage and testing
if __name__ == "__main__":
    # Test with sample job description
    sample_job_description = """
    Software Engineer - Python Developer
    
    We are looking for a skilled Python Developer to join our team.
    
    Requirements:
    - 3+ years of experience in Python development
    - Strong knowledge of Django and Flask frameworks
    - Experience with PostgreSQL and Redis
    - Familiarity with AWS cloud services
    - Bachelor's degree in Computer Science or related field
    
    Preferred:
    - Experience with React.js
    - Knowledge of Docker and Kubernetes
    - Agile development experience
    
    Responsibilities:
    - Develop and maintain web applications
    - Collaborate with cross-functional teams
    - Write clean, maintainable code
    - Participate in code reviews
    """
    
    parser = JobDescriptionParser()
    requirements = parser.parse_job_description(
        sample_job_description,
        job_title="Software Engineer - Python Developer",
        company="Tech Company"
    )
    
    print("Extracted Requirements:")
    print(f"Programming Languages: {requirements.programming_languages}")
    print(f"Frameworks/Tools: {requirements.frameworks_tools}")
    print(f"Required Skills: {requirements.required_skills}")
    print(f"ATS Keywords: {requirements.ats_keywords}")
