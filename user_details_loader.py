#!/usr/bin/env python3
"""
📋 User Details Loader
Simple loader for user details from my_details.json or my_details.txt
"""

import json
import os
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

class UserDetailsLoader:
    """Load user details from simple configuration files"""
    
    def __init__(self, details_file: str = None):
        """Initialize with details file path"""
        self.details_file = details_file or self._find_details_file()
        self.details = {}
        self.load_details()
    
    def _find_details_file(self) -> str:
        """Find the user details file"""
        possible_files = [
            'my_details.json',
            'my_details.txt', 
            'user_details.json',
            'user_details.txt'
        ]
        
        for file_path in possible_files:
            if os.path.exists(file_path):
                return file_path
        
        # Return default if none found
        return 'my_details.json'
    
    def load_details(self) -> bool:
        """Load details from file"""
        if not os.path.exists(self.details_file):
            print(f"⚠️ Details file not found: {self.details_file}")
            print(f"Please create and fill out {self.details_file}")
            return False
        
        try:
            if self.details_file.endswith('.json'):
                return self._load_json()
            elif self.details_file.endswith('.txt'):
                return self._load_txt()
            else:
                print(f"❌ Unsupported file format: {self.details_file}")
                return False
        except Exception as e:
            print(f"❌ Error loading details: {str(e)}")
            return False
    
    def _load_json(self) -> bool:
        """Load from JSON file"""
        with open(self.details_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract main sections
        self.details = {
            'personal_info': data.get('personal_info', {}),
            'professional_info': data.get('professional_info', {}),
            'job_search_preferences': data.get('job_search_preferences', {}),
            'documents': data.get('documents', {}),
            'application_settings': data.get('application_settings', {})
        }
        
        return True
    
    def _load_txt(self) -> bool:
        """Load from text file"""
        with open(self.details_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse text format
        self.details = {
            'personal_info': {},
            'professional_info': {},
            'job_search_preferences': {},
            'documents': {},
            'application_settings': {}
        }
        
        # Personal info mappings
        personal_mappings = {
            'FULL_NAME': 'name',
            'EMAIL': 'email',
            'PHONE': 'phone',
            'LOCATION': 'location',
            'LINKEDIN': 'linkedin_url',
            'WEBSITE': 'website'
        }
        
        # Professional info mappings
        professional_mappings = {
            'CURRENT_JOB_TITLE': 'current_title',
            'YEARS_OF_EXPERIENCE': 'experience_years',
            'EDUCATION': 'education',
            'SUMMARY': 'summary'
        }
        
        # Job search mappings
        job_search_mappings = {
            'MINIMUM_SALARY': 'minimum_salary',
            'PREFERRED_SALARY': 'preferred_salary',
            'SALARY_CURRENCY': 'currency',
            'WORK_TYPE': 'work_type',
            'REMOTE_PREFERENCE': 'remote_preference',
            'EXPERIENCE_LEVEL': 'experience_level'
        }
        
        # Document mappings
        document_mappings = {
            'RESUME_PATH': 'resume_path',
            'COVER_LETTER_PATH': 'cover_letter_path',
            'PORTFOLIO_URL': 'portfolio_url'
        }
        
        # Application settings mappings
        app_settings_mappings = {
            'MAX_APPLICATIONS_PER_DAY': 'max_applications_per_day',
            'EASY_APPLY_ONLY': 'auto_apply_easy_apply_only'
        }
        
        # Parse single-line fields
        for field, key in personal_mappings.items():
            value = self._extract_field(content, field)
            if value:
                self.details['personal_info'][key] = value
        
        for field, key in professional_mappings.items():
            value = self._extract_field(content, field)
            if value:
                if key == 'experience_years':
                    try:
                        self.details['professional_info'][key] = int(value)
                    except ValueError:
                        self.details['professional_info'][key] = value
                else:
                    self.details['professional_info'][key] = value
        
        for field, key in job_search_mappings.items():
            value = self._extract_field(content, field)
            if value:
                if 'salary' in key.lower():
                    try:
                        self.details['job_search_preferences'][key] = int(value)
                    except ValueError:
                        self.details['job_search_preferences'][key] = value
                else:
                    self.details['job_search_preferences'][key] = value
        
        for field, key in document_mappings.items():
            value = self._extract_field(content, field)
            if value:
                self.details['documents'][key] = value
        
        for field, key in app_settings_mappings.items():
            value = self._extract_field(content, field)
            if value:
                if key == 'max_applications_per_day':
                    try:
                        self.details['application_settings'][key] = int(value)
                    except ValueError:
                        self.details['application_settings'][key] = value
                elif key == 'auto_apply_easy_apply_only':
                    self.details['application_settings'][key] = value.lower() in ['true', 'yes', '1']
                else:
                    self.details['application_settings'][key] = value
        
        # Parse multi-line fields
        self.details['professional_info']['skills'] = self._extract_list(content, 'SKILLS')
        self.details['professional_info']['certifications'] = self._extract_list(content, 'CERTIFICATIONS')
        self.details['job_search_preferences']['desired_roles'] = self._extract_list(content, 'DESIRED_ROLES')
        self.details['job_search_preferences']['preferred_locations'] = self._extract_list(content, 'PREFERRED_LOCATIONS')
        self.details['application_settings']['skip_companies'] = self._extract_list(content, 'SKIP_COMPANIES')
        self.details['application_settings']['preferred_companies'] = self._extract_list(content, 'PREFERRED_COMPANIES')
        
        return True
    
    def _extract_field(self, content: str, field_name: str) -> Optional[str]:
        """Extract single field value"""
        pattern = rf'^{field_name}:\s*(.+?)$'
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            # Skip placeholder text
            if not value.startswith(('YOUR ', 'your.', 'path/to/', 'https://your')):
                return value
        return None
    
    def _extract_list(self, content: str, field_name: str) -> List[str]:
        """Extract multi-line list values"""
        pattern = rf'^{field_name}:\s*\n((?:^.+$\n?)*?)(?=^\w+:|$)'
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if match:
            lines = match.group(1).strip().split('\n')
            items = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith(('Skill ', 'Job Title ', 'City ', 'Company ', 'Certification ')):
                    items.append(line)
            return items
        return []
    
    def get_personal_info(self) -> Dict[str, Any]:
        """Get personal information"""
        return self.details.get('personal_info', {})
    
    def get_professional_info(self) -> Dict[str, Any]:
        """Get professional information"""
        return self.details.get('professional_info', {})
    
    def get_job_preferences(self) -> Dict[str, Any]:
        """Get job search preferences"""
        return self.details.get('job_search_preferences', {})
    
    def get_documents(self) -> Dict[str, Any]:
        """Get document paths"""
        return self.details.get('documents', {})
    
    def get_application_settings(self) -> Dict[str, Any]:
        """Get application settings"""
        return self.details.get('application_settings', {})
    
    def get_field_value(self, field_name: str, section: str = None) -> str:
        """Get specific field value for form filling"""
        # Common field mappings for job applications
        field_mappings = {
            'name': ('personal_info', 'name'),
            'full_name': ('personal_info', 'name'),
            'first_name': ('personal_info', 'name'),  # Will extract first name
            'last_name': ('personal_info', 'name'),   # Will extract last name
            'email': ('personal_info', 'email'),
            'phone': ('personal_info', 'phone'),
            'location': ('personal_info', 'location'),
            'city': ('personal_info', 'location'),
            'linkedin': ('personal_info', 'linkedin_url'),
            'website': ('personal_info', 'website'),
            'current_title': ('professional_info', 'current_title'),
            'job_title': ('professional_info', 'current_title'),
            'experience': ('professional_info', 'experience_years'),
            'summary': ('professional_info', 'summary'),
            'education': ('professional_info', 'education'),
            'skills': ('professional_info', 'skills'),
            'resume': ('documents', 'resume_path'),
            'cover_letter': ('documents', 'cover_letter_path')
        }
        
        field_key = field_name.lower().replace(' ', '_').replace('-', '_')
        
        if field_key in field_mappings:
            section_name, key = field_mappings[field_key]
            value = self.details.get(section_name, {}).get(key, '')
            
            # Handle special cases
            if field_key == 'first_name' and value:
                return value.split()[0] if value else ''
            elif field_key == 'last_name' and value:
                parts = value.split()
                return parts[-1] if len(parts) > 1 else ''
            elif field_key == 'skills' and isinstance(value, list):
                return ', '.join(value)
            
            return str(value) if value else ''
        
        return ''
    
    def is_configured(self) -> bool:
        """Check if user has configured their details"""
        personal = self.get_personal_info()
        return bool(personal.get('name') and personal.get('email') and 
                   not personal.get('name', '').startswith('YOUR'))
    
    def print_summary(self):
        """Print summary of loaded details"""
        print("📋 User Details Summary:")
        print("-" * 30)
        
        personal = self.get_personal_info()
        if personal.get('name'):
            print(f"👤 Name: {personal.get('name')}")
            print(f"📧 Email: {personal.get('email')}")
            print(f"📱 Phone: {personal.get('phone', 'Not provided')}")
            print(f"📍 Location: {personal.get('location', 'Not provided')}")
        else:
            print("❌ Personal information not configured")
        
        professional = self.get_professional_info()
        if professional.get('current_title'):
            print(f"💼 Title: {professional.get('current_title')}")
            print(f"⏱️ Experience: {professional.get('experience_years', 'Not specified')} years")
        
        if self.is_configured():
            print("✅ Details are configured and ready to use!")
        else:
            print("⚠️ Please fill out your details in the configuration file")


def test_loader():
    """Test the details loader"""
    loader = UserDetailsLoader()
    loader.print_summary()
    
    # Test field access
    print(f"\nField access test:")
    print(f"Name: {loader.get_field_value('name')}")
    print(f"Email: {loader.get_field_value('email')}")
    print(f"First Name: {loader.get_field_value('first_name')}")


if __name__ == "__main__":
    test_loader()
