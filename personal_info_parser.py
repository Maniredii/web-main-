#!/usr/bin/env python3
"""
📄 Personal Information File Parser
Parses personal information from various file formats (JSON, CSV, TXT)
"""

import json
import csv
import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from profile_manager import PersonalInfo, ProfileValidator

logger = logging.getLogger(__name__)


class PersonalInfoParser:
    """Parser for personal information files"""
    
    @staticmethod
    def parse_file(file_path: str) -> Tuple[Optional[PersonalInfo], List[str]]:
        """
        Parse personal information from file
        
        Args:
            file_path: Path to the personal information file
            
        Returns:
            Tuple of (PersonalInfo object or None, list of error messages)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return None, [f"File not found: {file_path}"]
        
        try:
            # Determine file type and parse accordingly
            if file_path.suffix.lower() == '.json':
                return PersonalInfoParser._parse_json(file_path)
            elif file_path.suffix.lower() == '.csv':
                return PersonalInfoParser._parse_csv(file_path)
            elif file_path.suffix.lower() in ['.txt', '.text']:
                return PersonalInfoParser._parse_txt(file_path)
            else:
                # Try to auto-detect format
                return PersonalInfoParser._auto_detect_and_parse(file_path)
                
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            return None, [f"Error parsing file: {str(e)}"]
    
    @staticmethod
    def _parse_json(file_path: Path) -> Tuple[Optional[PersonalInfo], List[str]]:
        """Parse JSON format personal info file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract personal information section
            if 'personal_information' in data:
                personal_data = data['personal_information']
            elif 'personal_info' in data:
                personal_data = data['personal_info']
            else:
                # Assume the whole file is personal info
                personal_data = data
            
            # Clean and validate data
            cleaned_data = PersonalInfoParser._clean_personal_data(personal_data)

            # Remove additional info before creating PersonalInfo object
            additional_info = cleaned_data.pop('_additional_info', {})

            personal_info = PersonalInfo(**cleaned_data)

            # Store additional info as an attribute for later use
            if additional_info:
                personal_info._additional_info = additional_info

            # Validate the parsed data
            errors = PersonalInfoParser._validate_personal_info(personal_info)
            
            return personal_info, errors
            
        except json.JSONDecodeError as e:
            return None, [f"Invalid JSON format: {str(e)}"]
        except Exception as e:
            return None, [f"Error parsing JSON: {str(e)}"]
    
    @staticmethod
    def _parse_csv(file_path: Path) -> Tuple[Optional[PersonalInfo], List[str]]:
        """Parse CSV format personal info file"""
        try:
            personal_data = {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                # Skip comment lines
                lines = [line for line in f if not line.strip().startswith('#')]
                
            # Reset file pointer and read CSV
            csv_content = '\n'.join(lines)
            csv_reader = csv.DictReader(csv_content.splitlines())
            
            for row in csv_reader:
                field = row.get('Field', '').strip().lower()
                value = row.get('Your Information', '').strip()
                
                if field and value:
                    personal_data[field] = value
            
            # Clean and validate data
            cleaned_data = PersonalInfoParser._clean_personal_data(personal_data)

            # Remove additional info before creating PersonalInfo object
            additional_info = cleaned_data.pop('_additional_info', {})

            personal_info = PersonalInfo(**cleaned_data)

            # Store additional info as an attribute for later use
            if additional_info:
                personal_info._additional_info = additional_info

            # Validate the parsed data
            errors = PersonalInfoParser._validate_personal_info(personal_info)
            
            return personal_info, errors
            
        except Exception as e:
            return None, [f"Error parsing CSV: {str(e)}"]
    
    @staticmethod
    def _parse_txt(file_path: Path) -> Tuple[Optional[PersonalInfo], List[str]]:
        """Parse text format personal info file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            personal_data = {}
            
            # Parse field patterns
            patterns = {
                'name': r'NAME:\s*(.+?)(?:\n|$)',
                'email': r'EMAIL:\s*(.+?)(?:\n|$)',
                'phone': r'PHONE:\s*(.+?)(?:\n|$)',
                'location': r'LOCATION:\s*(.+?)(?:\n|$)',
                'linkedin_url': r'LINKEDIN:\s*(.+?)(?:\n|$)',
                'website': r'WEBSITE:\s*(.+?)(?:\n|$)',
                'github': r'GITHUB:\s*(.+?)(?:\n|$)'
            }
            
            for field, pattern in patterns.items():
                match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    if value:
                        personal_data[field] = value
            
            # Parse additional URLs
            additional_urls_match = re.search(
                r'ADDITIONAL_URLS:\s*\n((?:.*\n?)*?)(?:\n\n|\n#|$)', 
                content, 
                re.IGNORECASE | re.MULTILINE
            )
            if additional_urls_match:
                urls_text = additional_urls_match.group(1).strip()
                urls = [url.strip() for url in urls_text.split('\n') if url.strip() and not url.strip().startswith('#')]
                if urls:
                    personal_data['additional_urls'] = urls
            
            # Clean and validate data
            cleaned_data = PersonalInfoParser._clean_personal_data(personal_data)

            # Remove additional info before creating PersonalInfo object
            additional_info = cleaned_data.pop('_additional_info', {})

            personal_info = PersonalInfo(**cleaned_data)

            # Store additional info as an attribute for later use
            if additional_info:
                personal_info._additional_info = additional_info

            # Validate the parsed data
            errors = PersonalInfoParser._validate_personal_info(personal_info)
            
            return personal_info, errors
            
        except Exception as e:
            return None, [f"Error parsing text file: {str(e)}"]
    
    @staticmethod
    def _auto_detect_and_parse(file_path: Path) -> Tuple[Optional[PersonalInfo], List[str]]:
        """Auto-detect file format and parse"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try JSON first
            try:
                json.loads(content)
                return PersonalInfoParser._parse_json(file_path)
            except json.JSONDecodeError:
                pass
            
            # Try CSV format
            if ',' in content and ('Field' in content or 'field' in content):
                return PersonalInfoParser._parse_csv(file_path)
            
            # Try text format
            if any(pattern in content.upper() for pattern in ['NAME:', 'EMAIL:', 'PHONE:']):
                return PersonalInfoParser._parse_txt(file_path)
            
            return None, ["Could not detect file format. Supported formats: JSON, CSV, TXT"]
            
        except Exception as e:
            return None, [f"Error auto-detecting format: {str(e)}"]
    
    @staticmethod
    def _clean_personal_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize personal data"""
        cleaned = {}
        
        # Field mapping for different naming conventions
        field_mapping = {
            'name': ['name', 'full_name', 'fullname', 'full name'],
            'email': ['email', 'email_address', 'mail', 'e-mail'],
            'phone': ['phone', 'phone_number', 'telephone', 'tel', 'mobile'],
            'location': ['location', 'address', 'city', 'residence'],
            'linkedin_url': ['linkedin_url', 'linkedin', 'linkedin_profile', 'linkedin url'],
            'website': ['website', 'personal_website', 'portfolio', 'homepage', 'web site']
        }

        # Additional fields that might be in the data but not in PersonalInfo
        additional_fields = ['github', 'github_url', 'github_profile', 'additional_urls']
        
        # Map fields
        for target_field, possible_names in field_mapping.items():
            for name in possible_names:
                if name in data or name.lower() in data:
                    value = data.get(name) or data.get(name.lower())
                    if value and str(value).strip():
                        cleaned[target_field] = str(value).strip()
                        break
        
        # Handle additional URLs and GitHub (store as additional info)
        additional_info = {}

        # Handle GitHub separately since it's not in PersonalInfo
        for field in additional_fields:
            if field in data:
                value = data[field]
                if value:
                    if field == 'additional_urls':
                        if isinstance(value, list):
                            additional_info[field] = [url.strip() for url in value if url.strip()]
                        elif isinstance(value, str):
                            additional_info[field] = [url.strip() for url in value.split('\n') if url.strip()]
                    else:
                        additional_info[field] = str(value).strip()

        # Clean and validate URLs
        url_fields = ['linkedin_url', 'website']
        for field in url_fields:
            if field in cleaned:
                cleaned[field] = PersonalInfoParser._clean_url(cleaned[field])

        # Store additional info for later use (could be used by calling code)
        if additional_info:
            cleaned['_additional_info'] = additional_info
        
        return cleaned
    
    @staticmethod
    def _clean_url(url: str) -> str:
        """Clean and validate URL"""
        url = url.strip()
        
        # Add https:// if missing
        if url and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    @staticmethod
    def _validate_personal_info(personal_info: PersonalInfo) -> List[str]:
        """Validate personal information"""
        errors = []
        
        # Required fields
        if not personal_info.name:
            errors.append("Name is required")
        
        if not personal_info.email:
            errors.append("Email is required")
        
        # Email validation
        if personal_info.email:
            is_valid, error = ProfileValidator.validate_email(personal_info.email)
            if not is_valid:
                errors.append(f"Email validation error: {error}")
        
        # Phone validation
        if personal_info.phone:
            is_valid, error = ProfileValidator.validate_phone(personal_info.phone)
            if not is_valid:
                errors.append(f"Phone validation error: {error}")
        
        # URL validations
        url_fields = [
            ('linkedin_url', 'LinkedIn URL'),
            ('website', 'Website URL'),
            ('github', 'GitHub URL')
        ]
        
        for field_name, display_name in url_fields:
            url = getattr(personal_info, field_name, None)
            if url:
                is_valid, error = ProfileValidator.validate_url(url)
                if not is_valid:
                    errors.append(f"{display_name} validation error: {error}")
        
        return errors
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """Get list of supported file formats"""
        return ['.json', '.csv', '.txt', '.text']
    
    @staticmethod
    def create_template_files(output_dir: str = ".") -> List[str]:
        """Create template files in the specified directory"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        created_files = []
        
        # Template files are already created in the main directory
        template_files = [
            'personal_info_template.json',
            'personal_info_template.csv', 
            'personal_info_template.txt'
        ]
        
        for template_file in template_files:
            source_path = Path(template_file)
            dest_path = output_path / template_file
            
            if source_path.exists():
                import shutil
                shutil.copy2(source_path, dest_path)
                created_files.append(str(dest_path))
        
        return created_files


def test_parser():
    """Test the parser with sample data"""
    # Test JSON parsing
    sample_json = {
        "personal_information": {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1-555-123-4567",
            "location": "Test City, TS, USA"
        }
    }
    
    # Create temporary test file
    test_file = Path("test_personal_info.json")
    with open(test_file, 'w') as f:
        json.dump(sample_json, f)
    
    try:
        personal_info, errors = PersonalInfoParser.parse_file(str(test_file))
        print(f"Parsed: {personal_info}")
        print(f"Errors: {errors}")
    finally:
        if test_file.exists():
            test_file.unlink()


if __name__ == "__main__":
    test_parser()
