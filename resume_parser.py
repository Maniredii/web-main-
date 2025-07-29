"""
Resume Parser and Analyzer for ATS Optimization
Parses existing resumes and analyzes content for optimization
"""

import os
import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import docx
import PyPDF2
import pdfplumber
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ResumeContent:
    """Structured resume content for analysis and optimization"""
    # Personal Information
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    
    # Professional Summary
    summary: str = ""
    objective: str = ""
    
    # Experience
    work_experience: List[Dict[str, Any]] = None
    
    # Education
    education: List[Dict[str, str]] = None
    
    # Skills
    technical_skills: List[str] = None
    soft_skills: List[str] = None
    programming_languages: List[str] = None
    frameworks_tools: List[str] = None
    
    # Additional Sections
    certifications: List[str] = None
    projects: List[Dict[str, str]] = None
    achievements: List[str] = None
    publications: List[str] = None
    
    # Metadata
    file_path: str = ""
    file_type: str = ""
    parsed_date: str = ""
    word_count: int = 0
    
    # ATS Analysis
    ats_score: float = 0.0
    keyword_density: Dict[str, float] = None
    formatting_issues: List[str] = None
    optimization_suggestions: List[str] = None
    
    def __post_init__(self):
        """Initialize empty lists for None fields"""
        for field_name, field_type in self.__annotations__.items():
            if getattr(self, field_name) is None:
                if hasattr(field_type, '__origin__') and field_type.__origin__ is list:
                    setattr(self, field_name, [])
                elif hasattr(field_type, '__origin__') and field_type.__origin__ is dict:
                    setattr(self, field_name, {})

class ResumeParser:
    """Intelligent resume parser with ATS analysis capabilities"""
    
    def __init__(self, ollama_client=None):
        self.ollama_client = ollama_client
        
        # Common skill patterns for extraction
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
            'soft_skills': [
                'leadership', 'communication', 'teamwork', 'problem solving',
                'project management', 'analytical thinking', 'creativity', 'adaptability'
            ]
        }
        
        # ATS-friendly formatting rules
        self.ats_rules = {
            'max_word_count': 800,
            'min_word_count': 300,
            'recommended_sections': [
                'contact information', 'professional summary', 'work experience',
                'education', 'skills'
            ],
            'avoid_elements': [
                'images', 'graphics', 'tables', 'text boxes', 'headers/footers'
            ]
        }
    
    def parse_resume(self, file_path: str) -> Optional[ResumeContent]:
        """
        Parse resume from file (DOCX or PDF)
        
        Args:
            file_path: Path to resume file
            
        Returns:
            ResumeContent object with parsed information
        """
        if not os.path.exists(file_path):
            logger.error(f"Resume file not found: {file_path}")
            return None
        
        file_ext = Path(file_path).suffix.lower()
        logger.info(f"Parsing resume: {file_path} ({file_ext})")
        
        try:
            if file_ext == '.docx':
                text = self._parse_docx(file_path)
            elif file_ext == '.pdf':
                text = self._parse_pdf(file_path)
            else:
                logger.error(f"Unsupported file format: {file_ext}")
                return None
            
            if not text:
                logger.error("Failed to extract text from resume")
                return None
            
            # Parse content from extracted text
            resume_content = self._parse_text_content(text)
            
            # Set metadata
            resume_content.file_path = file_path
            resume_content.file_type = file_ext
            resume_content.parsed_date = datetime.now().isoformat()
            resume_content.word_count = len(text.split())
            
            # Perform ATS analysis
            self._analyze_ats_compatibility(resume_content, text)
            
            logger.info(f"Successfully parsed resume with ATS score: {resume_content.ats_score:.2f}")
            return resume_content
            
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            return None
    
    def _parse_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text_parts = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text.strip())
            
            return '\n'.join(text_parts)
            
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            return ""
    
    def _parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(file_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                if text_parts:
                    return '\n'.join(text_parts)
            
            # Fallback to PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_parts = []
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                return '\n'.join(text_parts)
                
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            return ""
    
    def _parse_text_content(self, text: str) -> ResumeContent:
        """Parse structured content from resume text"""
        resume = ResumeContent()
        
        # Clean text
        text = self._clean_text(text)
        
        # Extract personal information
        resume.name = self._extract_name(text)
        resume.email = self._extract_email(text)
        resume.phone = self._extract_phone(text)
        resume.linkedin_url = self._extract_linkedin(text)
        resume.github_url = self._extract_github(text)
        
        # Extract sections
        resume.summary = self._extract_summary(text)
        resume.work_experience = self._extract_work_experience(text)
        resume.education = self._extract_education(text)
        resume.certifications = self._extract_certifications(text)
        resume.projects = self._extract_projects(text)
        
        # Extract skills
        resume.technical_skills = self._extract_technical_skills(text)
        resume.programming_languages = self._extract_skills(text, self.skill_patterns['programming_languages'])
        resume.frameworks_tools = self._extract_skills(text, self.skill_patterns['frameworks_tools'])
        resume.soft_skills = self._extract_skills(text, self.skill_patterns['soft_skills'])
        
        return resume
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize resume text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with parsing
        text = re.sub(r'[^\w\s@.\-+():/]', ' ', text)
        
        return text.strip()
    
    def _extract_name(self, text: str) -> str:
        """Extract candidate name from resume"""
        lines = text.split('\n')
        
        # Usually the name is in the first few lines
        for line in lines[:5]:
            line = line.strip()
            # Look for lines with 2-4 words, likely to be a name
            words = line.split()
            if 2 <= len(words) <= 4 and all(word.isalpha() for word in words):
                return line
        
        return ""
    
    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
            r'\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return ""
    
    def _extract_linkedin(self, text: str) -> str:
        """Extract LinkedIn URL"""
        linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
        match = re.search(linkedin_pattern, text, re.IGNORECASE)
        return f"https://{match.group(0)}" if match else ""
    
    def _extract_github(self, text: str) -> str:
        """Extract GitHub URL"""
        github_pattern = r'github\.com/[\w\-]+'
        match = re.search(github_pattern, text, re.IGNORECASE)
        return f"https://{match.group(0)}" if match else ""
    
    def _extract_summary(self, text: str) -> str:
        """Extract professional summary or objective"""
        summary_patterns = [
            r'(?:professional\s+)?summary[:\s]+(.*?)(?:\n\s*\n|experience|education)',
            r'objective[:\s]+(.*?)(?:\n\s*\n|experience|education)',
            r'profile[:\s]+(.*?)(?:\n\s*\n|experience|education)'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()
                # Clean up the summary
                summary = re.sub(r'\s+', ' ', summary)
                return summary[:500]  # Limit length
        
        return ""
    
    def _extract_work_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience entries"""
        experience = []
        
        # Look for experience section
        exp_pattern = r'(?:work\s+)?experience[:\s]+(.*?)(?:education|skills|projects|\Z)'
        match = re.search(exp_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            exp_text = match.group(1)
            
            # Split by common job entry patterns
            job_entries = re.split(r'\n(?=\w+.*\d{4})', exp_text)
            
            for entry in job_entries:
                if len(entry.strip()) > 20:  # Filter out short entries
                    job_info = self._parse_job_entry(entry)
                    if job_info:
                        experience.append(job_info)
        
        return experience
    
    def _parse_job_entry(self, entry: str) -> Optional[Dict[str, Any]]:
        """Parse individual job entry"""
        lines = [line.strip() for line in entry.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        job_info = {
            'title': '',
            'company': '',
            'duration': '',
            'description': ''
        }
        
        # First line usually contains title and company
        first_line = lines[0]
        
        # Look for date patterns to separate title/company from dates
        date_pattern = r'\d{4}'
        if re.search(date_pattern, first_line):
            parts = re.split(r'\s+(?=\d{4})', first_line)
            if len(parts) >= 2:
                job_info['title'] = parts[0].strip()
                job_info['duration'] = parts[1].strip()
        else:
            job_info['title'] = first_line
        
        # Look for company in subsequent lines
        for line in lines[1:3]:  # Check next 2 lines
            if not re.search(r'\d{4}', line) and len(line) > 3:
                job_info['company'] = line
                break
        
        # Combine remaining lines as description
        desc_lines = []
        for line in lines[1:]:
            if line != job_info['company'] and not re.match(r'^\d{4}', line):
                desc_lines.append(line)
        
        job_info['description'] = ' '.join(desc_lines)
        
        return job_info if job_info['title'] else None
    
    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information"""
        education = []
        
        edu_pattern = r'education[:\s]+(.*?)(?:experience|skills|projects|\Z)'
        match = re.search(edu_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            edu_text = match.group(1)
            
            # Look for degree patterns
            degree_patterns = [
                r'(bachelor|master|phd|doctorate).*?(?:in\s+)?([\w\s]+?)(?:\d{4}|\n)',
                r'(b\.?s\.?|m\.?s\.?|ph\.?d\.?).*?(?:in\s+)?([\w\s]+?)(?:\d{4}|\n)'
            ]
            
            for pattern in degree_patterns:
                matches = re.finditer(pattern, edu_text, re.IGNORECASE)
                for match in matches:
                    education.append({
                        'degree': match.group(1),
                        'field': match.group(2).strip() if match.group(2) else '',
                        'institution': '',  # Could be enhanced to extract institution
                        'year': ''
                    })
        
        return education
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        cert_patterns = [
            r'certifications?[:\s]+(.*?)(?:\n\s*\n|skills|projects|\Z)',
            r'certificates?[:\s]+(.*?)(?:\n\s*\n|skills|projects|\Z)'
        ]
        
        certifications = []
        for pattern in cert_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                cert_text = match.group(1)
                # Split by common delimiters
                certs = re.split(r'[,;\n•\-]', cert_text)
                for cert in certs:
                    cert = cert.strip()
                    if len(cert) > 3:
                        certifications.append(cert)
        
        return certifications
    
    def _extract_projects(self, text: str) -> List[Dict[str, str]]:
        """Extract project information"""
        projects = []
        
        proj_pattern = r'projects?[:\s]+(.*?)(?:\n\s*\n|skills|education|\Z)'
        match = re.search(proj_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            proj_text = match.group(1)
            
            # Split by project entries (look for project names)
            project_entries = re.split(r'\n(?=[A-Z])', proj_text)
            
            for entry in project_entries:
                if len(entry.strip()) > 10:
                    lines = entry.strip().split('\n')
                    projects.append({
                        'name': lines[0].strip(),
                        'description': ' '.join(lines[1:]).strip() if len(lines) > 1 else ''
                    })
        
        return projects
    
    def _extract_technical_skills(self, text: str) -> List[str]:
        """Extract technical skills section"""
        skills = []
        
        skills_patterns = [
            r'(?:technical\s+)?skills[:\s]+(.*?)(?:\n\s*\n|experience|education|\Z)',
            r'technologies[:\s]+(.*?)(?:\n\s*\n|experience|education|\Z)'
        ]
        
        for pattern in skills_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                skills_text = match.group(1)
                # Split by common delimiters
                skill_list = re.split(r'[,;•\n\-]', skills_text)
                for skill in skill_list:
                    skill = skill.strip()
                    if len(skill) > 1 and len(skill) < 30:
                        skills.append(skill)
        
        return skills
    
    def _extract_skills(self, text: str, skill_list: List[str]) -> List[str]:
        """Extract specific skills from predefined list"""
        found_skills = []
        text_lower = text.lower()
        
        for skill in skill_list:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _analyze_ats_compatibility(self, resume: ResumeContent, text: str):
        """Analyze resume for ATS compatibility"""
        score = 0.0
        issues = []
        suggestions = []
        
        # Check word count
        if resume.word_count < self.ats_rules['min_word_count']:
            issues.append(f"Resume too short ({resume.word_count} words)")
            suggestions.append("Add more detail to experience and skills sections")
        elif resume.word_count > self.ats_rules['max_word_count']:
            issues.append(f"Resume too long ({resume.word_count} words)")
            suggestions.append("Condense content to focus on most relevant information")
        else:
            score += 20
        
        # Check for required sections
        section_score = 0
        if resume.name:
            section_score += 10
        else:
            issues.append("Missing candidate name")
        
        if resume.email:
            section_score += 10
        else:
            issues.append("Missing email address")
        
        if resume.work_experience:
            section_score += 20
        else:
            issues.append("Missing work experience section")
        
        if resume.technical_skills or resume.programming_languages:
            section_score += 20
        else:
            issues.append("Missing technical skills section")
            suggestions.append("Add a dedicated skills section with relevant technologies")
        
        if resume.education:
            section_score += 10
        else:
            suggestions.append("Consider adding education section")
        
        score += section_score
        
        # Check for keywords density
        if resume.technical_skills:
            score += 20
        
        # Final score calculation
        resume.ats_score = min(score, 100.0)
        resume.formatting_issues = issues
        resume.optimization_suggestions = suggestions
    
    def save_resume_analysis(self, resume: ResumeContent, filepath: str):
        """Save resume analysis to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(asdict(resume), f, indent=2)
            logger.info(f"Resume analysis saved to: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save resume analysis: {e}")

# Example usage
if __name__ == "__main__":
    parser = ResumeParser()
    
    # Test with sample resume file
    resume_path = "sample resume.docx"
    if os.path.exists(resume_path):
        resume_content = parser.parse_resume(resume_path)
        if resume_content:
            print(f"Parsed resume for: {resume_content.name}")
            print(f"ATS Score: {resume_content.ats_score:.2f}/100")
            print(f"Technical Skills: {resume_content.technical_skills}")
            print(f"Programming Languages: {resume_content.programming_languages}")
    else:
        print(f"Resume file not found: {resume_path}")
