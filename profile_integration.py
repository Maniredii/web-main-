#!/usr/bin/env python3
"""
🔗 Profile Integration Module
Seamless integration between profile manager and LinkedIn automation
"""

import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from profile_manager import (
    UserProfile, PersonalInfo, ProfessionalInfo, 
    SearchCriteria, DocumentPaths, ProfileStorage
)

logger = logging.getLogger(__name__)


class ProfileIntegration:
    """Integration layer between profile manager and automation"""
    
    def __init__(self, profile_path: str = "user_profile.json"):
        self.profile_path = profile_path
        self.storage = ProfileStorage()
        self._profile_cache = None
    
    def get_profile(self) -> Optional[UserProfile]:
        """Get current user profile"""
        if self._profile_cache is None:
            self._profile_cache = self.storage.load_profile(self.profile_path)
        return self._profile_cache
    
    def refresh_profile(self):
        """Refresh profile cache"""
        self._profile_cache = None
        return self.get_profile()
    
    def convert_to_legacy_format(self) -> Optional[Dict[str, Any]]:
        """Convert new profile format to legacy automation format"""
        profile = self.get_profile()
        if not profile:
            return None
        
        # Convert to the format expected by linkedin_ollama_automation.py
        legacy_profile = {
            "personal_info": {
                "name": profile.personal_info.name,
                "email": profile.personal_info.email,
                "phone": profile.personal_info.phone,
                "location": profile.personal_info.location,
                "linkedin_url": profile.personal_info.linkedin_url,
                "website": profile.personal_info.website
            },
            "professional_info": {
                "current_title": profile.professional_info.current_title,
                "experience_years": profile.professional_info.experience_years,
                "skills": profile.professional_info.skills,
                "education": profile.professional_info.education,
                "desired_salary": profile.professional_info.desired_salary,
                "summary": profile.professional_info.summary,
                "certifications": profile.professional_info.certifications
            },
            "search_criteria": {
                "keywords": profile.search_criteria.keywords,
                "location": profile.search_criteria.location,
                "experience_level": profile.search_criteria.experience_level,
                "remote_preference": profile.search_criteria.remote_preference,
                "max_applications": profile.search_criteria.max_applications,
                "salary_range": profile.search_criteria.salary_range,
                "job_types": profile.search_criteria.job_types
            },
            "document_paths": {
                "resume_path": profile.document_paths.resume_path,
                "cover_letter_path": profile.document_paths.cover_letter_path,
                "portfolio_path": profile.document_paths.portfolio_path
            },
            # Legacy fields for backward compatibility
            "skills": profile.professional_info.skills,
            "experience_years": profile.professional_info.experience_years,
            "resume_path": profile.document_paths.resume_path,
            "cover_letter_path": profile.document_paths.cover_letter_path,
            "remote_preference": profile.search_criteria.remote_preference,
            "desired_salary": profile.professional_info.desired_salary,
            "education": profile.professional_info.education
        }
        
        return legacy_profile
    
    def save_legacy_profile(self, output_path: str = "user_profile.json") -> bool:
        """Save profile in legacy format for automation"""
        try:
            legacy_profile = self.convert_to_legacy_format()
            if not legacy_profile:
                logger.error("No profile available to convert")
                return False
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(legacy_profile, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Legacy profile saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save legacy profile: {e}")
            return False


class FormFieldMapper:
    """Maps profile data to common form fields"""
    
    def __init__(self, profile: UserProfile):
        self.profile = profile
    
    def get_field_mapping(self) -> Dict[str, Any]:
        """Get comprehensive field mapping for form filling"""
        return {
            # Personal Information Fields
            "name": self.profile.personal_info.name,
            "full_name": self.profile.personal_info.name,
            "first_name": self._get_first_name(),
            "last_name": self._get_last_name(),
            "fname": self._get_first_name(),
            "lname": self._get_last_name(),
            "given_name": self._get_first_name(),
            "family_name": self._get_last_name(),
            "surname": self._get_last_name(),
            
            # Contact Information
            "email": self.profile.personal_info.email,
            "email_address": self.profile.personal_info.email,
            "mail": self.profile.personal_info.email,
            "phone": self.profile.personal_info.phone,
            "phone_number": self.profile.personal_info.phone,
            "telephone": self.profile.personal_info.phone,
            "mobile": self.profile.personal_info.phone,
            "tel": self.profile.personal_info.phone,
            
            # Location Information
            "location": self.profile.personal_info.location,
            "address": self.profile.personal_info.location,
            "city": self._get_city(),
            "state": self._get_state(),
            "country": self._get_country(),
            
            # Professional Information
            "current_title": self.profile.professional_info.current_title,
            "job_title": self.profile.professional_info.current_title,
            "position": self.profile.professional_info.current_title,
            "title": self.profile.professional_info.current_title,
            "experience": str(self.profile.professional_info.experience_years),
            "experience_years": str(self.profile.professional_info.experience_years),
            "years_experience": str(self.profile.professional_info.experience_years),
            "work_experience": str(self.profile.professional_info.experience_years),
            
            # Education
            "education": self.profile.professional_info.education,
            "education_level": self.profile.professional_info.education,
            "degree": self.profile.professional_info.education,
            "highest_education": self.profile.professional_info.education,
            
            # Salary Information
            "salary": self.profile.professional_info.desired_salary,
            "desired_salary": self.profile.professional_info.desired_salary,
            "expected_salary": self.profile.professional_info.desired_salary,
            "compensation": self.profile.professional_info.desired_salary,
            "salary_expectation": self.profile.professional_info.desired_salary,
            
            # Skills and Summary
            "skills": ", ".join(self.profile.professional_info.skills),
            "key_skills": ", ".join(self.profile.professional_info.skills),
            "technical_skills": ", ".join(self.profile.professional_info.skills),
            "summary": self.profile.professional_info.summary,
            "professional_summary": self.profile.professional_info.summary,
            "about": self.profile.professional_info.summary,
            "bio": self.profile.professional_info.summary,
            
            # URLs
            "linkedin": self.profile.personal_info.linkedin_url,
            "linkedin_url": self.profile.personal_info.linkedin_url,
            "linkedin_profile": self.profile.personal_info.linkedin_url,
            "website": self.profile.personal_info.website,
            "personal_website": self.profile.personal_info.website,
            "portfolio": self.profile.document_paths.portfolio_path,
            "portfolio_url": self.profile.document_paths.portfolio_path,
            
            # Work Preferences
            "remote_work": "Yes" if self.profile.search_criteria.remote_preference else "No",
            "willing_to_relocate": "No",  # Default assumption
            "available_start_date": "Immediately",  # Default
            
            # File Paths
            "resume_path": self.profile.document_paths.resume_path,
            "cv_path": self.profile.document_paths.resume_path,
            "cover_letter_path": self.profile.document_paths.cover_letter_path,
        }
    
    def get_field_value(self, field_identifier: str, field_label: str = "") -> str:
        """Get value for a specific field based on identifier and label"""
        field_mapping = self.get_field_mapping()
        
        # Normalize field identifier
        field_key = field_identifier.lower().strip()
        field_text = f"{field_identifier} {field_label}".lower()
        
        # Direct mapping lookup
        if field_key in field_mapping:
            return str(field_mapping[field_key])
        
        # Fuzzy matching based on common patterns
        for pattern, value in field_mapping.items():
            if pattern in field_text:
                return str(value)
        
        # Special handling for common field patterns
        if any(term in field_text for term in ['first', 'fname', 'given']):
            return self._get_first_name()
        elif any(term in field_text for term in ['last', 'lname', 'surname', 'family']):
            return self._get_last_name()
        elif any(term in field_text for term in ['email', 'mail']):
            return self.profile.personal_info.email
        elif any(term in field_text for term in ['phone', 'tel', 'mobile']):
            return self.profile.personal_info.phone
        elif any(term in field_text for term in ['experience', 'years']):
            return str(self.profile.professional_info.experience_years)
        elif any(term in field_text for term in ['salary', 'compensation']):
            return self.profile.professional_info.desired_salary
        elif any(term in field_text for term in ['location', 'city', 'address']):
            return self.profile.personal_info.location
        elif any(term in field_text for term in ['education', 'degree']):
            return self.profile.professional_info.education
        elif any(term in field_text for term in ['skills', 'technical']):
            return ", ".join(self.profile.professional_info.skills)
        elif any(term in field_text for term in ['summary', 'about', 'bio']):
            return self.profile.professional_info.summary
        
        return ""
    
    def _get_first_name(self) -> str:
        """Extract first name from full name"""
        name_parts = self.profile.personal_info.name.split()
        return name_parts[0] if name_parts else ""
    
    def _get_last_name(self) -> str:
        """Extract last name from full name"""
        name_parts = self.profile.personal_info.name.split()
        return name_parts[-1] if len(name_parts) > 1 else ""
    
    def _get_city(self) -> str:
        """Extract city from location"""
        location_parts = self.profile.personal_info.location.split(',')
        return location_parts[0].strip() if location_parts else ""
    
    def _get_state(self) -> str:
        """Extract state from location"""
        location_parts = self.profile.personal_info.location.split(',')
        return location_parts[1].strip() if len(location_parts) > 1 else ""
    
    def _get_country(self) -> str:
        """Extract country from location"""
        location_parts = self.profile.personal_info.location.split(',')
        return location_parts[-1].strip() if len(location_parts) > 2 else "United States"


class AutomationProfileAdapter:
    """Adapter to make profile manager work with existing automation"""
    
    def __init__(self, profile_path: str = "user_profile.json"):
        self.integration = ProfileIntegration(profile_path)
        self.profile = self.integration.get_profile()
        self.field_mapper = FormFieldMapper(self.profile) if self.profile else None
    
    def get_automation_config(self) -> Dict[str, Any]:
        """Get configuration for automation system"""
        if not self.profile:
            return {}
        
        return {
            "email": self.profile.personal_info.email,
            "keywords": self.profile.search_criteria.keywords[0] if self.profile.search_criteria.keywords else "Software Engineer",
            "location": self.profile.search_criteria.location,
            "experience_level": self.profile.search_criteria.experience_level,
            "max_applications": self.profile.search_criteria.max_applications,
            "remote_preference": self.profile.search_criteria.remote_preference,
            "resume_path": self.profile.document_paths.resume_path,
            "cover_letter_path": self.profile.document_paths.cover_letter_path
        }
    
    def get_form_field_value(self, field_name: str, field_label: str = "", field_type: str = "") -> str:
        """Get value for form field - compatible with existing automation"""
        if not self.field_mapper:
            return ""
        
        return self.field_mapper.get_field_value(field_name, field_label)
    
    def get_profile_dict(self) -> Dict[str, Any]:
        """Get profile as dictionary - compatible with existing automation"""
        return self.integration.convert_to_legacy_format() or {}
    
    def ensure_legacy_compatibility(self) -> bool:
        """Ensure legacy profile file exists for automation"""
        return self.integration.save_legacy_profile()


def setup_profile_integration():
    """Setup profile integration for automation"""
    try:
        adapter = AutomationProfileAdapter()
        
        # Ensure legacy profile exists
        if adapter.ensure_legacy_compatibility():
            logger.info("✅ Profile integration setup complete")
            return adapter
        else:
            logger.warning("⚠️ Failed to setup profile integration")
            return None
            
    except Exception as e:
        logger.error(f"❌ Profile integration setup failed: {e}")
        return None


if __name__ == "__main__":
    # Test integration
    adapter = setup_profile_integration()
    if adapter:
        config = adapter.get_automation_config()
        print("🔧 Automation Configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")
    else:
        print("❌ Integration setup failed")
