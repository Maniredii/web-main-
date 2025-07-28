#!/usr/bin/env python3
"""
🔧 LinkedIn Profile Manager
Comprehensive user profile management system for LinkedIn automation
"""

import json
import os
import re
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from pathlib import Path
import hashlib
import base64
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Personal info file parser
try:
    from personal_info_parser import PersonalInfoParser
    PARSER_AVAILABLE = True
except ImportError:
    PARSER_AVAILABLE = False
    logger.warning("Personal info parser not available")


@dataclass
class PersonalInfo:
    """Personal information data structure"""
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin_url: str = ""
    website: str = ""


@dataclass
class ProfessionalInfo:
    """Professional information data structure"""
    current_title: str = ""
    experience_years: int = 0
    skills: List[str] = None
    education: str = ""
    certifications: List[str] = None
    desired_salary: str = ""
    summary: str = ""
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.certifications is None:
            self.certifications = []


@dataclass
class SearchCriteria:
    """Job search criteria data structure"""
    keywords: List[str] = None
    location: str = ""
    experience_level: str = "Mid-Senior level"
    remote_preference: bool = True
    salary_range: str = ""
    job_types: List[str] = None
    max_applications: int = 10
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.job_types is None:
            self.job_types = ["Full-time"]


@dataclass
class DocumentPaths:
    """Document file paths"""
    resume_path: str = ""
    cover_letter_path: str = ""
    portfolio_path: str = ""


@dataclass
class UserProfile:
    """Complete user profile"""
    personal_info: PersonalInfo = None
    professional_info: ProfessionalInfo = None
    search_criteria: SearchCriteria = None
    document_paths: DocumentPaths = None
    created_at: str = ""
    updated_at: str = ""
    version: str = "1.0"
    
    def __post_init__(self):
        if self.personal_info is None:
            self.personal_info = PersonalInfo()
        if self.professional_info is None:
            self.professional_info = ProfessionalInfo()
        if self.search_criteria is None:
            self.search_criteria = SearchCriteria()
        if self.document_paths is None:
            self.document_paths = DocumentPaths()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()


class ProfileValidator:
    """Profile data validation"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format"""
        if not email:
            return False, "Email is required"
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """Validate phone number format"""
        if not phone:
            return True, ""  # Phone is optional
        
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        if len(digits_only) < 10:
            return False, "Phone number must have at least 10 digits"
        
        return True, ""

    @staticmethod
    def validate_url(url: str) -> Tuple[bool, str]:
        """Validate URL format"""
        if not url:
            return True, ""  # URLs are optional

        # Basic URL validation
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, url):
            return False, "Invalid URL format (must start with http:// or https://)"

        return True, ""

    @staticmethod
    def validate_file_path(file_path: str, file_type: str) -> Tuple[bool, str]:
        """Validate file path exists"""
        if not file_path:
            return True, ""  # File paths are optional
        
        if not os.path.exists(file_path):
            return False, f"{file_type} file not found: {file_path}"
        
        # Check file extension for resume/cover letter
        if file_type.lower() in ["resume", "cover letter"]:
            valid_extensions = ['.pdf', '.doc', '.docx', '.txt']
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in valid_extensions:
                return False, f"{file_type} must be PDF, DOC, DOCX, or TXT format"
        
        return True, ""
    
    @staticmethod
    def validate_profile(profile: UserProfile) -> Tuple[bool, List[str]]:
        """Validate complete profile"""
        errors = []
        
        # Validate personal info
        if not profile.personal_info.name.strip():
            errors.append("Name is required")
        
        email_valid, email_error = ProfileValidator.validate_email(profile.personal_info.email)
        if not email_valid:
            errors.append(email_error)
        
        phone_valid, phone_error = ProfileValidator.validate_phone(profile.personal_info.phone)
        if not phone_valid:
            errors.append(phone_error)
        
        # Validate professional info
        if profile.professional_info.experience_years < 0:
            errors.append("Experience years cannot be negative")
        
        if not profile.professional_info.skills:
            errors.append("At least one skill is required")
        
        # Validate search criteria
        if not profile.search_criteria.keywords:
            errors.append("At least one job keyword is required")
        
        if profile.search_criteria.max_applications <= 0:
            errors.append("Maximum applications must be greater than 0")
        
        # Validate file paths
        for file_type, file_path in [
            ("Resume", profile.document_paths.resume_path),
            ("Cover Letter", profile.document_paths.cover_letter_path),
            ("Portfolio", profile.document_paths.portfolio_path)
        ]:
            file_valid, file_error = ProfileValidator.validate_file_path(file_path, file_type)
            if not file_valid:
                errors.append(file_error)
        
        return len(errors) == 0, errors


class ProfileSecurity:
    """Handle profile security and encryption"""
    
    def __init__(self, password: Optional[str] = None):
        self.password = password
        self.key = self._generate_key() if password else None
    
    def _generate_key(self) -> bytes:
        """Generate encryption key from password"""
        password_bytes = self.password.encode('utf-8')
        key = hashlib.pbkdf2_hmac('sha256', password_bytes, b'salt_', 100000)
        return base64.urlsafe_b64encode(key)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt profile data"""
        if not self.key:
            return data
        
        fernet = Fernet(self.key)
        encrypted_data = fernet.encrypt(data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt profile data"""
        if not self.key:
            return encrypted_data
        
        try:
            fernet = Fernet(self.key)
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = fernet.decrypt(decoded_data)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("Invalid password or corrupted data")


class ProfileStorage:
    """Handle profile storage and backup"""
    
    def __init__(self, profile_dir: str = "profiles"):
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(exist_ok=True)
        self.backup_dir = self.profile_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def save_profile(self, profile: UserProfile, filename: str = "user_profile.json", 
                    security: Optional[ProfileSecurity] = None) -> bool:
        """Save profile to JSON file"""
        try:
            # Convert profile to dictionary
            profile_dict = self._profile_to_dict(profile)
            
            # Convert to JSON string
            json_data = json.dumps(profile_dict, indent=2, ensure_ascii=False)
            
            # Encrypt if security is provided
            if security:
                json_data = security.encrypt_data(json_data)
                filename = filename.replace('.json', '.encrypted')
            
            # Save to file
            file_path = self.profile_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            logger.info(f"Profile saved to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")
            return False
    
    def load_profile(self, filename: str = "user_profile.json", 
                    security: Optional[ProfileSecurity] = None) -> Optional[UserProfile]:
        """Load profile from JSON file"""
        try:
            file_path = self.profile_dir / filename
            
            # Try encrypted file if regular file doesn't exist
            if not file_path.exists():
                encrypted_path = self.profile_dir / filename.replace('.json', '.encrypted')
                if encrypted_path.exists():
                    file_path = encrypted_path
                else:
                    logger.warning(f"Profile file not found: {filename}")
                    return None
            
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()
            
            # Decrypt if needed
            if security and file_path.suffix == '.encrypted':
                data = security.decrypt_data(data)
            
            # Parse JSON
            profile_dict = json.loads(data)
            
            # Convert to UserProfile object
            profile = self._dict_to_profile(profile_dict)
            
            logger.info(f"Profile loaded from: {file_path}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to load profile: {e}")
            return None
    
    def backup_profile(self, filename: str = "user_profile.json") -> bool:
        """Create backup of current profile"""
        try:
            source_path = self.profile_dir / filename
            if not source_path.exists():
                return False
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{source_path.stem}_{timestamp}{source_path.suffix}"
            backup_path = self.backup_dir / backup_filename
            
            shutil.copy2(source_path, backup_path)
            logger.info(f"Profile backed up to: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup profile: {e}")
            return False
    
    def list_profiles(self) -> List[str]:
        """List all available profiles"""
        profiles = []
        for file_path in self.profile_dir.glob("*.json"):
            profiles.append(file_path.name)
        for file_path in self.profile_dir.glob("*.encrypted"):
            profiles.append(file_path.name)
        return sorted(profiles)
    
    def list_backups(self) -> List[str]:
        """List all backup files"""
        backups = []
        for file_path in self.backup_dir.glob("*"):
            backups.append(file_path.name)
        return sorted(backups, reverse=True)
    
    def _profile_to_dict(self, profile: UserProfile) -> Dict[str, Any]:
        """Convert UserProfile to dictionary"""
        return {
            "personal_info": asdict(profile.personal_info),
            "professional_info": asdict(profile.professional_info),
            "search_criteria": asdict(profile.search_criteria),
            "document_paths": asdict(profile.document_paths),
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
            "version": profile.version
        }
    
    def _dict_to_profile(self, data: Dict[str, Any]) -> UserProfile:
        """Convert dictionary to UserProfile"""
        return UserProfile(
            personal_info=PersonalInfo(**data.get("personal_info", {})),
            professional_info=ProfessionalInfo(**data.get("professional_info", {})),
            search_criteria=SearchCriteria(**data.get("search_criteria", {})),
            document_paths=DocumentPaths(**data.get("document_paths", {})),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            version=data.get("version", "1.0")
        )


class ProfileTemplates:
    """Pre-defined profile templates for different job types"""

    @staticmethod
    def get_software_engineer_template() -> UserProfile:
        """Software Engineer profile template"""
        profile = UserProfile()
        profile.professional_info.skills = [
            "Python", "JavaScript", "React", "Node.js", "SQL", "Git",
            "AWS", "Docker", "REST APIs", "Agile"
        ]
        profile.search_criteria.keywords = [
            "Software Engineer", "Full Stack Developer", "Backend Developer",
            "Python Developer", "JavaScript Developer"
        ]
        profile.search_criteria.experience_level = "Mid-Senior level"
        profile.professional_info.current_title = "Software Engineer"
        return profile

    @staticmethod
    def get_data_scientist_template() -> UserProfile:
        """Data Scientist profile template"""
        profile = UserProfile()
        profile.professional_info.skills = [
            "Python", "R", "SQL", "Machine Learning", "TensorFlow", "PyTorch",
            "Pandas", "NumPy", "Scikit-learn", "Tableau", "Power BI", "Statistics"
        ]
        profile.search_criteria.keywords = [
            "Data Scientist", "Machine Learning Engineer", "Data Analyst",
            "AI Engineer", "Research Scientist"
        ]
        profile.search_criteria.experience_level = "Mid-Senior level"
        profile.professional_info.current_title = "Data Scientist"
        return profile

    @staticmethod
    def get_product_manager_template() -> UserProfile:
        """Product Manager profile template"""
        profile = UserProfile()
        profile.professional_info.skills = [
            "Product Strategy", "Agile", "Scrum", "User Research", "Analytics",
            "Roadmapping", "Stakeholder Management", "A/B Testing", "SQL", "Jira"
        ]
        profile.search_criteria.keywords = [
            "Product Manager", "Senior Product Manager", "Product Owner",
            "Technical Product Manager", "Product Lead"
        ]
        profile.search_criteria.experience_level = "Mid-Senior level"
        profile.professional_info.current_title = "Product Manager"
        return profile

    @staticmethod
    def get_marketing_template() -> UserProfile:
        """Marketing Specialist profile template"""
        profile = UserProfile()
        profile.professional_info.skills = [
            "Digital Marketing", "SEO", "SEM", "Social Media", "Content Marketing",
            "Google Analytics", "Facebook Ads", "Email Marketing", "CRM", "Copywriting"
        ]
        profile.search_criteria.keywords = [
            "Marketing Manager", "Digital Marketing Specialist", "Marketing Coordinator",
            "Content Marketing Manager", "Growth Marketing"
        ]
        profile.search_criteria.experience_level = "Mid-Senior level"
        profile.professional_info.current_title = "Marketing Specialist"
        return profile

    @staticmethod
    def get_available_templates() -> Dict[str, callable]:
        """Get all available templates"""
        return {
            "Software Engineer": ProfileTemplates.get_software_engineer_template,
            "Data Scientist": ProfileTemplates.get_data_scientist_template,
            "Product Manager": ProfileTemplates.get_product_manager_template,
            "Marketing Specialist": ProfileTemplates.get_marketing_template
        }


class ProfileManagerGUI:
    """GUI interface for profile management"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LinkedIn Profile Manager")
        self.root.geometry("800x600")

        # Initialize components
        self.storage = ProfileStorage()
        self.validator = ProfileValidator()
        self.current_profile = UserProfile()
        self.security = None

        # Create GUI
        self.create_widgets()
        self.load_existing_profile()

    def create_widgets(self):
        """Create GUI widgets"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.create_personal_tab()
        self.create_professional_tab()
        self.create_search_tab()
        self.create_documents_tab()
        self.create_templates_tab()
        self.create_security_tab()

        # Create bottom frame for buttons
        self.create_bottom_frame()

    def create_personal_tab(self):
        """Create personal information tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Personal Info")

        # Create form fields
        row = 0

        # Name
        ttk.Label(frame, text="Full Name *:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=40).grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # Email
        ttk.Label(frame, text="Email *:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.email_var, width=40).grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # Phone
        ttk.Label(frame, text="Phone:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.phone_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.phone_var, width=40).grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # Location
        ttk.Label(frame, text="Location:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.location_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.location_var, width=40).grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # LinkedIn URL
        ttk.Label(frame, text="LinkedIn URL:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.linkedin_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.linkedin_var, width=40).grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # Website
        ttk.Label(frame, text="Website:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.website_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.website_var, width=40).grid(row=row, column=1, padx=5, pady=5)

    def create_professional_tab(self):
        """Create professional information tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Professional")

        row = 0

        # Current Title
        ttk.Label(frame, text="Current Title:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.title_var, width=40).grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # Experience Years
        ttk.Label(frame, text="Years of Experience:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.experience_var = tk.IntVar()
        ttk.Spinbox(frame, from_=0, to=50, textvariable=self.experience_var, width=10).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1

        # Skills
        ttk.Label(frame, text="Skills * (one per line):").grid(row=row, column=0, sticky=tk.NW, padx=5, pady=5)
        self.skills_text = tk.Text(frame, width=40, height=8)
        self.skills_text.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # Education
        ttk.Label(frame, text="Education:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.education_var = tk.StringVar()
        education_combo = ttk.Combobox(frame, textvariable=self.education_var, width=37)
        education_combo['values'] = [
            "High School", "Associate's Degree", "Bachelor's Degree",
            "Master's Degree", "MBA", "PhD", "Other"
        ]
        education_combo.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # Desired Salary
        ttk.Label(frame, text="Desired Salary:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.salary_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.salary_var, width=40).grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # Import from file section
        ttk.Separator(frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', padx=5, pady=10)
        row += 1

        ttk.Label(frame, text="Import Personal Info:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        row += 1

        import_frame = ttk.Frame(frame)
        import_frame.grid(row=row, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        ttk.Button(import_frame, text="Load from File", command=self.import_personal_info).pack(side=tk.LEFT, padx=5)
        ttk.Button(import_frame, text="Create Templates", command=self.create_personal_info_templates).pack(side=tk.LEFT, padx=5)

        # Status label for import operations
        self.import_status_label = ttk.Label(frame, text="", foreground="blue")
        self.import_status_label.grid(row=row+1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        # Summary
        ttk.Label(frame, text="Professional Summary:").grid(row=row, column=0, sticky=tk.NW, padx=5, pady=5)
        self.summary_text = tk.Text(frame, width=40, height=6)
        self.summary_text.grid(row=row, column=1, padx=5, pady=5)

    def create_search_tab(self):
        """Create job search criteria tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Job Search")

        row = 0

        # Keywords
        ttk.Label(frame, text="Job Keywords * (one per line):").grid(row=row, column=0, sticky=tk.NW, padx=5, pady=5)
        self.keywords_text = tk.Text(frame, width=40, height=6)
        self.keywords_text.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # Preferred Location
        ttk.Label(frame, text="Preferred Location:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.search_location_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.search_location_var, width=40).grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # Experience Level
        ttk.Label(frame, text="Experience Level:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.exp_level_var = tk.StringVar()
        exp_combo = ttk.Combobox(frame, textvariable=self.exp_level_var, width=37)
        exp_combo['values'] = [
            "Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"
        ]
        exp_combo.set("Mid-Senior level")
        exp_combo.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # Remote Preference
        self.remote_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Open to Remote Work", variable=self.remote_var).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1

        # Max Applications
        ttk.Label(frame, text="Max Applications per Run:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_apps_var = tk.IntVar(value=10)
        ttk.Spinbox(frame, from_=1, to=100, textvariable=self.max_apps_var, width=10).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1

        # Salary Range
        ttk.Label(frame, text="Salary Range:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.salary_range_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.salary_range_var, width=40).grid(row=row, column=1, padx=5, pady=5)

    def create_documents_tab(self):
        """Create documents tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Documents")

        row = 0

        # Resume
        ttk.Label(frame, text="Resume File:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.resume_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.resume_var, width=50).grid(row=row, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse", command=lambda: self.browse_file(self.resume_var, "Resume")).grid(row=row, column=2, padx=5, pady=5)
        row += 1

        # Cover Letter
        ttk.Label(frame, text="Cover Letter Template:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.cover_letter_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.cover_letter_var, width=50).grid(row=row, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse", command=lambda: self.browse_file(self.cover_letter_var, "Cover Letter")).grid(row=row, column=2, padx=5, pady=5)
        row += 1

        # Portfolio
        ttk.Label(frame, text="Portfolio/Website:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.portfolio_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.portfolio_var, width=50).grid(row=row, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse", command=lambda: self.browse_file(self.portfolio_var, "Portfolio")).grid(row=row, column=2, padx=5, pady=5)
        row += 1

        # File validation status
        self.file_status_label = ttk.Label(frame, text="", foreground="green")
        self.file_status_label.grid(row=row, column=1, sticky=tk.W, padx=5, pady=10)

    def create_templates_tab(self):
        """Create templates tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Templates")

        # Instructions
        ttk.Label(frame, text="Choose a template to pre-fill your profile:", font=("Arial", 12, "bold")).pack(pady=10)

        # Template buttons
        templates = ProfileTemplates.get_available_templates()
        for template_name, template_func in templates.items():
            btn = ttk.Button(frame, text=f"Load {template_name} Template",
                           command=lambda tf=template_func: self.load_template(tf))
            btn.pack(pady=5, padx=20, fill=tk.X)

        # Warning
        warning_text = "⚠️ Loading a template will overwrite your current professional and search criteria data."
        ttk.Label(frame, text=warning_text, foreground="orange", wraplength=400).pack(pady=20)

        # Custom template section
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=20)
        ttk.Label(frame, text="Save Current Profile as Template:", font=("Arial", 10, "bold")).pack(pady=5)

        template_frame = ttk.Frame(frame)
        template_frame.pack(pady=5)

        ttk.Label(template_frame, text="Template Name:").pack(side=tk.LEFT, padx=5)
        self.template_name_var = tk.StringVar()
        ttk.Entry(template_frame, textvariable=self.template_name_var, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(template_frame, text="Save Template", command=self.save_as_template).pack(side=tk.LEFT, padx=5)

    def create_security_tab(self):
        """Create security tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Security")

        # Encryption section
        ttk.Label(frame, text="Profile Encryption", font=("Arial", 12, "bold")).pack(pady=10)

        self.encryption_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Enable profile encryption", variable=self.encryption_var,
                       command=self.toggle_encryption).pack(pady=5)

        # Password frame
        self.password_frame = ttk.Frame(frame)
        self.password_frame.pack(pady=10)

        ttk.Label(self.password_frame, text="Encryption Password:").pack(side=tk.LEFT, padx=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self.password_frame, textvariable=self.password_var, show="*", width=20)
        self.password_entry.pack(side=tk.LEFT, padx=5)

        # Initially hide password frame
        self.password_frame.pack_forget()

        # Privacy options
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=20)
        ttk.Label(frame, text="Privacy Options", font=("Arial", 12, "bold")).pack(pady=10)

        self.exclude_phone_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Exclude phone number from automation",
                       variable=self.exclude_phone_var).pack(anchor=tk.W, padx=20, pady=2)

        self.exclude_salary_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Exclude salary information from automation",
                       variable=self.exclude_salary_var).pack(anchor=tk.W, padx=20, pady=2)

        # Backup section
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=20)
        ttk.Label(frame, text="Backup & Export", font=("Arial", 12, "bold")).pack(pady=10)

        backup_frame = ttk.Frame(frame)
        backup_frame.pack(pady=5)

        ttk.Button(backup_frame, text="Create Backup", command=self.create_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(backup_frame, text="Export Profile", command=self.export_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(backup_frame, text="Import Profile", command=self.import_profile).pack(side=tk.LEFT, padx=5)

    def create_bottom_frame(self):
        """Create bottom frame with action buttons"""
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.X, padx=10, pady=5)

        # Left side - status
        self.status_label = ttk.Label(frame, text="Ready", foreground="green")
        self.status_label.pack(side=tk.LEFT)

        # Right side - buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(side=tk.RIGHT)

        ttk.Button(button_frame, text="Validate", command=self.validate_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Profile", command=self.save_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Profile", command=self.load_profile_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="New Profile", command=self.new_profile).pack(side=tk.LEFT, padx=5)

    def browse_file(self, var: tk.StringVar, file_type: str):
        """Browse for file"""
        filetypes = [
            ("All supported", "*.pdf;*.doc;*.docx;*.txt"),
            ("PDF files", "*.pdf"),
            ("Word files", "*.doc;*.docx"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title=f"Select {file_type} File",
            filetypes=filetypes
        )

        if filename:
            var.set(filename)
            self.validate_files()

    def validate_files(self):
        """Validate all file paths"""
        files_to_check = [
            ("Resume", self.resume_var.get()),
            ("Cover Letter", self.cover_letter_var.get()),
            ("Portfolio", self.portfolio_var.get())
        ]

        errors = []
        for file_type, file_path in files_to_check:
            if file_path:
                valid, error = ProfileValidator.validate_file_path(file_path, file_type)
                if not valid:
                    errors.append(error)

        if errors:
            self.file_status_label.config(text="⚠️ File validation errors", foreground="red")
        else:
            self.file_status_label.config(text="✅ All files valid", foreground="green")

    def toggle_encryption(self):
        """Toggle encryption password field"""
        if self.encryption_var.get():
            self.password_frame.pack(pady=10)
        else:
            self.password_frame.pack_forget()
            self.security = None

    def load_template(self, template_func):
        """Load a profile template"""
        if messagebox.askyesno("Load Template",
                              "This will overwrite your current professional and search data. Continue?"):
            template_profile = template_func()

            # Load professional info
            self.title_var.set(template_profile.professional_info.current_title)
            self.experience_var.set(template_profile.professional_info.experience_years)
            self.skills_text.delete(1.0, tk.END)
            self.skills_text.insert(1.0, "\n".join(template_profile.professional_info.skills))
            self.education_var.set(template_profile.professional_info.education)
            self.salary_var.set(template_profile.professional_info.desired_salary)

            # Load search criteria
            self.keywords_text.delete(1.0, tk.END)
            self.keywords_text.insert(1.0, "\n".join(template_profile.search_criteria.keywords))
            self.exp_level_var.set(template_profile.search_criteria.experience_level)
            self.remote_var.set(template_profile.search_criteria.remote_preference)
            self.max_apps_var.set(template_profile.search_criteria.max_applications)

            self.status_label.config(text="Template loaded successfully", foreground="green")

    def save_as_template(self):
        """Save current profile as template"""
        template_name = self.template_name_var.get().strip()
        if not template_name:
            messagebox.showerror("Error", "Please enter a template name")
            return

        # Get current profile data
        profile = self.get_profile_from_form()

        # Save as template
        template_filename = f"template_{template_name.lower().replace(' ', '_')}.json"
        if self.storage.save_profile(profile, template_filename):
            messagebox.showinfo("Success", f"Template saved as {template_filename}")
            self.template_name_var.set("")
        else:
            messagebox.showerror("Error", "Failed to save template")

    def get_profile_from_form(self) -> UserProfile:
        """Get profile data from form fields"""
        profile = UserProfile()

        # Personal info
        profile.personal_info.name = self.name_var.get().strip()
        profile.personal_info.email = self.email_var.get().strip()
        profile.personal_info.phone = self.phone_var.get().strip()
        profile.personal_info.location = self.location_var.get().strip()
        profile.personal_info.linkedin_url = self.linkedin_var.get().strip()
        profile.personal_info.website = self.website_var.get().strip()

        # Professional info
        profile.professional_info.current_title = self.title_var.get().strip()
        profile.professional_info.experience_years = self.experience_var.get()
        profile.professional_info.skills = [s.strip() for s in self.skills_text.get(1.0, tk.END).strip().split('\n') if s.strip()]
        profile.professional_info.education = self.education_var.get().strip()
        profile.professional_info.desired_salary = self.salary_var.get().strip()
        profile.professional_info.summary = self.summary_text.get(1.0, tk.END).strip()

        # Search criteria
        profile.search_criteria.keywords = [k.strip() for k in self.keywords_text.get(1.0, tk.END).strip().split('\n') if k.strip()]
        profile.search_criteria.location = self.search_location_var.get().strip()
        profile.search_criteria.experience_level = self.exp_level_var.get()
        profile.search_criteria.remote_preference = self.remote_var.get()
        profile.search_criteria.max_applications = self.max_apps_var.get()
        profile.search_criteria.salary_range = self.salary_range_var.get().strip()

        # Document paths
        profile.document_paths.resume_path = self.resume_var.get().strip()
        profile.document_paths.cover_letter_path = self.cover_letter_var.get().strip()
        profile.document_paths.portfolio_path = self.portfolio_var.get().strip()

        return profile

    def set_form_from_profile(self, profile: UserProfile):
        """Set form fields from profile data"""
        # Personal info
        self.name_var.set(profile.personal_info.name)
        self.email_var.set(profile.personal_info.email)
        self.phone_var.set(profile.personal_info.phone)
        self.location_var.set(profile.personal_info.location)
        self.linkedin_var.set(profile.personal_info.linkedin_url)
        self.website_var.set(profile.personal_info.website)

        # Professional info
        self.title_var.set(profile.professional_info.current_title)
        self.experience_var.set(profile.professional_info.experience_years)
        self.skills_text.delete(1.0, tk.END)
        self.skills_text.insert(1.0, '\n'.join(profile.professional_info.skills))
        self.education_var.set(profile.professional_info.education)
        self.salary_var.set(profile.professional_info.desired_salary)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, profile.professional_info.summary)

        # Search criteria
        self.keywords_text.delete(1.0, tk.END)
        self.keywords_text.insert(1.0, '\n'.join(profile.search_criteria.keywords))
        self.search_location_var.set(profile.search_criteria.location)
        self.exp_level_var.set(profile.search_criteria.experience_level)
        self.remote_var.set(profile.search_criteria.remote_preference)
        self.max_apps_var.set(profile.search_criteria.max_applications)
        self.salary_range_var.set(profile.search_criteria.salary_range)

        # Document paths
        self.resume_var.set(profile.document_paths.resume_path)
        self.cover_letter_var.set(profile.document_paths.cover_letter_path)
        self.portfolio_var.set(profile.document_paths.portfolio_path)

        # Validate files
        self.validate_files()

    def validate_profile(self):
        """Validate current profile"""
        profile = self.get_profile_from_form()
        is_valid, errors = ProfileValidator.validate_profile(profile)

        if is_valid:
            self.status_label.config(text="✅ Profile is valid", foreground="green")
            messagebox.showinfo("Validation", "Profile is valid and ready to use!")
        else:
            self.status_label.config(text="❌ Profile has errors", foreground="red")
            error_message = "Profile validation errors:\n\n" + "\n".join(f"• {error}" for error in errors)
            messagebox.showerror("Validation Errors", error_message)

    def save_profile(self):
        """Save current profile"""
        profile = self.get_profile_from_form()

        # Setup security if encryption is enabled
        security = None
        if self.encryption_var.get():
            password = self.password_var.get()
            if not password:
                messagebox.showerror("Error", "Please enter an encryption password")
                return
            security = ProfileSecurity(password)

        # Validate before saving
        is_valid, errors = ProfileValidator.validate_profile(profile)
        if not is_valid:
            if not messagebox.askyesno("Validation Errors",
                                     f"Profile has {len(errors)} validation errors. Save anyway?"):
                return

        # Save profile
        filename = "user_profile.json"
        if self.storage.save_profile(profile, filename, security):
            self.status_label.config(text="✅ Profile saved successfully", foreground="green")
            messagebox.showinfo("Success", f"Profile saved to {filename}")
            self.current_profile = profile
        else:
            self.status_label.config(text="❌ Failed to save profile", foreground="red")
            messagebox.showerror("Error", "Failed to save profile")

    def load_profile_dialog(self):
        """Load profile with file dialog"""
        profiles = self.storage.list_profiles()
        if not profiles:
            messagebox.showinfo("No Profiles", "No saved profiles found")
            return

        # Create selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Profile")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Select a profile to load:").pack(pady=10)

        # Profile listbox
        listbox = tk.Listbox(dialog, height=10)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        for profile in profiles:
            listbox.insert(tk.END, profile)

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        def load_selected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a profile")
                return

            filename = profiles[selection[0]]
            self.load_profile_file(filename)
            dialog.destroy()

        ttk.Button(button_frame, text="Load", command=load_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def load_profile_file(self, filename: str):
        """Load profile from file"""
        security = None

        # Check if file is encrypted
        if filename.endswith('.encrypted'):
            password = tk.simpledialog.askstring("Password", "Enter encryption password:", show='*')
            if not password:
                return
            security = ProfileSecurity(password)

        try:
            profile = self.storage.load_profile(filename, security)
            if profile:
                self.set_form_from_profile(profile)
                self.current_profile = profile
                self.status_label.config(text=f"✅ Loaded {filename}", foreground="green")
                messagebox.showinfo("Success", f"Profile loaded from {filename}")
            else:
                self.status_label.config(text="❌ Failed to load profile", foreground="red")
                messagebox.showerror("Error", "Failed to load profile")
        except ValueError as e:
            messagebox.showerror("Decryption Error", str(e))

    def load_existing_profile(self):
        """Load existing profile on startup"""
        profile = self.storage.load_profile()
        if profile:
            self.set_form_from_profile(profile)
            self.current_profile = profile
            self.status_label.config(text="✅ Existing profile loaded", foreground="green")

    def new_profile(self):
        """Create new profile"""
        if messagebox.askyesno("New Profile", "This will clear all current data. Continue?"):
            self.current_profile = UserProfile()
            self.set_form_from_profile(self.current_profile)
            self.status_label.config(text="Ready for new profile", foreground="blue")

    def create_backup(self):
        """Create backup of current profile"""
        if self.storage.backup_profile():
            messagebox.showinfo("Backup", "Profile backup created successfully")
        else:
            messagebox.showerror("Error", "Failed to create backup")

    def export_profile(self):
        """Export profile to chosen location"""
        filename = filedialog.asksaveasfilename(
            title="Export Profile",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            profile = self.get_profile_from_form()
            temp_storage = ProfileStorage(os.path.dirname(filename))
            if temp_storage.save_profile(profile, os.path.basename(filename)):
                messagebox.showinfo("Export", f"Profile exported to {filename}")
            else:
                messagebox.showerror("Error", "Failed to export profile")

    def import_profile(self):
        """Import profile from chosen file"""
        filename = filedialog.askopenfilename(
            title="Import Profile",
            filetypes=[("JSON files", "*.json"), ("Encrypted files", "*.encrypted"), ("All files", "*.*")]
        )

        if filename:
            # Copy to profiles directory
            dest_filename = os.path.basename(filename)
            dest_path = self.storage.profile_dir / dest_filename
            shutil.copy2(filename, dest_path)

            # Load the imported profile
            self.load_profile_file(dest_filename)

    def import_personal_info(self):
        """Import personal information from file"""
        if not PARSER_AVAILABLE:
            messagebox.showerror("Error", "Personal info parser not available. Please ensure personal_info_parser.py is in the same directory.")
            return

        # File dialog for selecting personal info file
        filetypes = [
            ("All supported", "*.json;*.csv;*.txt"),
            ("JSON files", "*.json"),
            ("CSV files", "*.csv"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Select Personal Information File",
            filetypes=filetypes
        )

        if not filename:
            return

        try:
            # Parse the file
            personal_info, errors = PersonalInfoParser.parse_file(filename)

            if personal_info:
                # Update the form fields
                self.name_var.set(personal_info.name)
                self.email_var.set(personal_info.email)
                self.phone_var.set(personal_info.phone)
                self.location_var.set(personal_info.location)
                self.linkedin_var.set(personal_info.linkedin_url)
                self.website_var.set(personal_info.website)

                # Show success message
                if errors:
                    warning_msg = f"Personal information imported with {len(errors)} warnings:\n\n" + "\n".join(f"• {error}" for error in errors)
                    messagebox.showwarning("Import Warnings", warning_msg)
                    self.import_status_label.config(text=f"✅ Imported with {len(errors)} warnings", foreground="orange")
                else:
                    messagebox.showinfo("Success", "Personal information imported successfully!")
                    self.import_status_label.config(text="✅ Personal info imported successfully", foreground="green")
            else:
                error_msg = "Failed to import personal information:\n\n" + "\n".join(f"• {error}" for error in errors)
                messagebox.showerror("Import Error", error_msg)
                self.import_status_label.config(text="❌ Import failed", foreground="red")

        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error during import: {str(e)}")
            self.import_status_label.config(text="❌ Import error", foreground="red")

    def create_personal_info_templates(self):
        """Create personal information template files"""
        try:
            # Ask user where to save templates
            directory = filedialog.askdirectory(
                title="Select Directory to Save Templates",
                initialdir=os.getcwd()
            )

            if not directory:
                return

            if PARSER_AVAILABLE:
                created_files = PersonalInfoParser.create_template_files(directory)
                if created_files:
                    files_list = "\n".join(f"• {os.path.basename(f)}" for f in created_files)
                    messagebox.showinfo("Templates Created", f"Template files created:\n\n{files_list}\n\nLocation: {directory}")
                    self.import_status_label.config(text="✅ Templates created", foreground="green")
                else:
                    messagebox.showwarning("Warning", "No template files were created")
                    self.import_status_label.config(text="⚠️ Template creation failed", foreground="orange")
            else:
                # Fallback: copy template files manually
                template_files = [
                    'personal_info_template.json',
                    'personal_info_template.csv',
                    'personal_info_template.txt'
                ]

                created_files = []
                for template_file in template_files:
                    source_path = Path(template_file)
                    dest_path = Path(directory) / template_file

                    if source_path.exists():
                        shutil.copy2(source_path, dest_path)
                        created_files.append(str(dest_path))

                if created_files:
                    files_list = "\n".join(f"• {os.path.basename(f)}" for f in created_files)
                    messagebox.showinfo("Templates Created", f"Template files created:\n\n{files_list}\n\nLocation: {directory}")
                    self.import_status_label.config(text="✅ Templates created", foreground="green")
                else:
                    messagebox.showerror("Error", "Template files not found in current directory")
                    self.import_status_label.config(text="❌ Templates not found", foreground="red")

        except Exception as e:
            messagebox.showerror("Error", f"Error creating templates: {str(e)}")
            self.import_status_label.config(text="❌ Template creation error", foreground="red")

    def run(self):
        """Run the GUI"""
        self.root.mainloop()


class ProfileManagerCLI:
    """Command-line interface for profile management"""

    def __init__(self):
        self.storage = ProfileStorage()
        self.validator = ProfileValidator()

    def run(self):
        """Run CLI interface"""
        print("🔧 LinkedIn Profile Manager CLI")
        print("=" * 40)

        while True:
            self.show_menu()
            choice = input("\nEnter your choice (1-10): ").strip()

            if choice == '1':
                self.create_new_profile()
            elif choice == '2':
                self.edit_existing_profile()
            elif choice == '3':
                self.validate_profile()
            elif choice == '4':
                self.list_profiles()
            elif choice == '5':
                self.load_template()
            elif choice == '6':
                self.import_personal_info_cli()
            elif choice == '7':
                self.create_personal_info_templates_cli()
            elif choice == '8':
                self.backup_profile()
            elif choice == '9':
                self.export_import_profile()
            elif choice == '10':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")

            input("\nPress Enter to continue...")

    def show_menu(self):
        """Show main menu"""
        print("\n📋 Main Menu:")
        print("1. Create New Profile")
        print("2. Edit Existing Profile")
        print("3. Validate Profile")
        print("4. List Saved Profiles")
        print("5. Load Template")
        print("6. Import Personal Info from File")
        print("7. Create Personal Info Templates")
        print("8. Backup Profile")
        print("9. Export/Import Profile")
        print("10. Exit")

    def create_new_profile(self):
        """Create new profile via CLI"""
        print("\n📝 Creating New Profile")
        print("-" * 25)

        profile = UserProfile()

        # Personal Information
        print("\n👤 Personal Information:")
        profile.personal_info.name = input("Full Name *: ").strip()
        profile.personal_info.email = input("Email *: ").strip()
        profile.personal_info.phone = input("Phone (optional): ").strip()
        profile.personal_info.location = input("Location: ").strip()
        profile.personal_info.linkedin_url = input("LinkedIn URL (optional): ").strip()

        # Professional Information
        print("\n💼 Professional Information:")
        profile.professional_info.current_title = input("Current Job Title: ").strip()

        try:
            profile.professional_info.experience_years = int(input("Years of Experience: ") or "0")
        except ValueError:
            profile.professional_info.experience_years = 0

        print("Skills (enter one per line, empty line to finish):")
        skills = []
        while True:
            skill = input("  Skill: ").strip()
            if not skill:
                break
            skills.append(skill)
        profile.professional_info.skills = skills

        profile.professional_info.education = input("Education Level: ").strip()
        profile.professional_info.desired_salary = input("Desired Salary (optional): ").strip()

        # Job Search Criteria
        print("\n🔍 Job Search Criteria:")
        print("Job Keywords (enter one per line, empty line to finish):")
        keywords = []
        while True:
            keyword = input("  Keyword: ").strip()
            if not keyword:
                break
            keywords.append(keyword)
        profile.search_criteria.keywords = keywords

        profile.search_criteria.location = input("Preferred Job Location: ").strip()

        print("Experience Level Options:")
        exp_levels = ["Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"]
        for i, level in enumerate(exp_levels, 1):
            print(f"  {i}. {level}")

        try:
            exp_choice = int(input("Choose experience level (1-6): ") or "4") - 1
            if 0 <= exp_choice < len(exp_levels):
                profile.search_criteria.experience_level = exp_levels[exp_choice]
        except ValueError:
            profile.search_criteria.experience_level = "Mid-Senior level"

        remote_pref = input("Open to remote work? (y/n): ").lower().startswith('y')
        profile.search_criteria.remote_preference = remote_pref

        try:
            profile.search_criteria.max_applications = int(input("Max applications per run (default 10): ") or "10")
        except ValueError:
            profile.search_criteria.max_applications = 10

        # Document Paths
        print("\n📄 Document Paths (optional):")
        profile.document_paths.resume_path = input("Resume file path: ").strip()
        profile.document_paths.cover_letter_path = input("Cover letter template path: ").strip()

        # Validate and save
        is_valid, errors = self.validator.validate_profile(profile)
        if not is_valid:
            print(f"\n⚠️ Profile has {len(errors)} validation errors:")
            for error in errors:
                print(f"  • {error}")

            if not input("\nSave anyway? (y/n): ").lower().startswith('y'):
                print("❌ Profile not saved")
                return

        if self.storage.save_profile(profile):
            print("✅ Profile created and saved successfully!")
        else:
            print("❌ Failed to save profile")

    def edit_existing_profile(self):
        """Edit existing profile"""
        profiles = self.storage.list_profiles()
        if not profiles:
            print("❌ No saved profiles found")
            return

        print("\n📝 Available Profiles:")
        for i, profile_name in enumerate(profiles, 1):
            print(f"  {i}. {profile_name}")

        try:
            choice = int(input(f"\nSelect profile to edit (1-{len(profiles)}): ")) - 1
            if 0 <= choice < len(profiles):
                filename = profiles[choice]
                profile = self.storage.load_profile(filename)
                if profile:
                    print(f"✅ Loaded {filename}")
                    self.edit_profile_fields(profile)

                    if self.storage.save_profile(profile, filename):
                        print("✅ Profile updated successfully!")
                    else:
                        print("❌ Failed to save profile")
                else:
                    print("❌ Failed to load profile")
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Invalid input")

    def edit_profile_fields(self, profile: UserProfile):
        """Edit specific profile fields"""
        while True:
            print("\n🔧 Edit Profile Fields:")
            print("1. Personal Information")
            print("2. Professional Information")
            print("3. Job Search Criteria")
            print("4. Document Paths")
            print("5. Done Editing")

            choice = input("\nSelect section to edit (1-5): ").strip()

            if choice == '1':
                self.edit_personal_info(profile.personal_info)
            elif choice == '2':
                self.edit_professional_info(profile.professional_info)
            elif choice == '3':
                self.edit_search_criteria(profile.search_criteria)
            elif choice == '4':
                self.edit_document_paths(profile.document_paths)
            elif choice == '5':
                break
            else:
                print("❌ Invalid choice")

    def edit_personal_info(self, personal_info: PersonalInfo):
        """Edit personal information"""
        print(f"\nCurrent Name: {personal_info.name}")
        new_name = input("New Name (Enter to keep current): ").strip()
        if new_name:
            personal_info.name = new_name

        print(f"Current Email: {personal_info.email}")
        new_email = input("New Email (Enter to keep current): ").strip()
        if new_email:
            personal_info.email = new_email

        print(f"Current Phone: {personal_info.phone}")
        new_phone = input("New Phone (Enter to keep current): ").strip()
        if new_phone:
            personal_info.phone = new_phone

        print(f"Current Location: {personal_info.location}")
        new_location = input("New Location (Enter to keep current): ").strip()
        if new_location:
            personal_info.location = new_location

    def edit_professional_info(self, professional_info: ProfessionalInfo):
        """Edit professional information"""
        print(f"\nCurrent Title: {professional_info.current_title}")
        new_title = input("New Title (Enter to keep current): ").strip()
        if new_title:
            professional_info.current_title = new_title

        print(f"Current Experience: {professional_info.experience_years} years")
        new_exp = input("New Experience Years (Enter to keep current): ").strip()
        if new_exp:
            try:
                professional_info.experience_years = int(new_exp)
            except ValueError:
                print("❌ Invalid number")

        print(f"Current Skills: {', '.join(professional_info.skills)}")
        if input("Update skills? (y/n): ").lower().startswith('y'):
            print("Enter new skills (one per line, empty line to finish):")
            skills = []
            while True:
                skill = input("  Skill: ").strip()
                if not skill:
                    break
                skills.append(skill)
            if skills:
                professional_info.skills = skills

    def edit_search_criteria(self, search_criteria: SearchCriteria):
        """Edit search criteria"""
        print(f"\nCurrent Keywords: {', '.join(search_criteria.keywords)}")
        if input("Update keywords? (y/n): ").lower().startswith('y'):
            print("Enter new keywords (one per line, empty line to finish):")
            keywords = []
            while True:
                keyword = input("  Keyword: ").strip()
                if not keyword:
                    break
                keywords.append(keyword)
            if keywords:
                search_criteria.keywords = keywords

        print(f"Current Max Applications: {search_criteria.max_applications}")
        new_max = input("New Max Applications (Enter to keep current): ").strip()
        if new_max:
            try:
                search_criteria.max_applications = int(new_max)
            except ValueError:
                print("❌ Invalid number")

    def edit_document_paths(self, document_paths: DocumentPaths):
        """Edit document paths"""
        print(f"\nCurrent Resume Path: {document_paths.resume_path}")
        new_resume = input("New Resume Path (Enter to keep current): ").strip()
        if new_resume:
            document_paths.resume_path = new_resume

        print(f"Current Cover Letter Path: {document_paths.cover_letter_path}")
        new_cover = input("New Cover Letter Path (Enter to keep current): ").strip()
        if new_cover:
            document_paths.cover_letter_path = new_cover

    def validate_profile(self):
        """Validate existing profile"""
        profile = self.storage.load_profile()
        if not profile:
            print("❌ No profile found to validate")
            return

        is_valid, errors = self.validator.validate_profile(profile)
        if is_valid:
            print("✅ Profile is valid and ready to use!")
        else:
            print(f"❌ Profile has {len(errors)} validation errors:")
            for error in errors:
                print(f"  • {error}")

    def list_profiles(self):
        """List all saved profiles"""
        profiles = self.storage.list_profiles()
        if not profiles:
            print("❌ No saved profiles found")
            return

        print("\n📋 Saved Profiles:")
        for i, profile_name in enumerate(profiles, 1):
            print(f"  {i}. {profile_name}")

        # Show backups too
        backups = self.storage.list_backups()
        if backups:
            print("\n💾 Available Backups:")
            for i, backup_name in enumerate(backups[:5], 1):  # Show only recent 5
                print(f"  {i}. {backup_name}")

    def load_template(self):
        """Load a profile template"""
        templates = ProfileTemplates.get_available_templates()

        print("\n📋 Available Templates:")
        template_list = list(templates.items())
        for i, (name, _) in enumerate(template_list, 1):
            print(f"  {i}. {name}")

        try:
            choice = int(input(f"\nSelect template (1-{len(template_list)}): ")) - 1
            if 0 <= choice < len(template_list):
                template_name, template_func = template_list[choice]
                profile = template_func()

                if self.storage.save_profile(profile, f"template_{template_name.lower().replace(' ', '_')}.json"):
                    print(f"✅ {template_name} template loaded and saved!")
                else:
                    print("❌ Failed to save template")
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Invalid input")

    def backup_profile(self):
        """Create profile backup"""
        if self.storage.backup_profile():
            print("✅ Profile backup created successfully!")
        else:
            print("❌ Failed to create backup")

    def export_import_profile(self):
        """Export or import profile"""
        print("\n📤📥 Export/Import:")
        print("1. Export Profile")
        print("2. Import Profile")

        choice = input("Select option (1-2): ").strip()

        if choice == '1':
            filename = input("Export filename (with .json extension): ").strip()
            if not filename.endswith('.json'):
                filename += '.json'

            profile = self.storage.load_profile()
            if profile:
                temp_storage = ProfileStorage(".")
                if temp_storage.save_profile(profile, filename):
                    print(f"✅ Profile exported to {filename}")
                else:
                    print("❌ Failed to export profile")
            else:
                print("❌ No profile to export")

        elif choice == '2':
            filename = input("Import filename: ").strip()
            if os.path.exists(filename):
                # Copy to profiles directory
                dest_filename = os.path.basename(filename)
                dest_path = self.storage.profile_dir / dest_filename
                shutil.copy2(filename, dest_path)
                print(f"✅ Profile imported as {dest_filename}")
            else:
                print("❌ File not found")
        else:
            print("❌ Invalid choice")

    def import_personal_info_cli(self):
        """Import personal information from file via CLI"""
        if not PARSER_AVAILABLE:
            print("❌ Personal info parser not available")
            print("Please ensure personal_info_parser.py is in the same directory")
            return

        print("\n📄 Import Personal Information from File")
        print("-" * 40)

        # Get file path
        file_path = input("Enter path to personal info file: ").strip()

        if not file_path:
            print("❌ No file path provided")
            return

        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return

        try:
            # Parse the file
            personal_info, errors = PersonalInfoParser.parse_file(file_path)

            if personal_info:
                print(f"\n✅ Personal information parsed successfully!")
                print(f"📋 Parsed Information:")
                print(f"  Name: {personal_info.name}")
                print(f"  Email: {personal_info.email}")
                print(f"  Phone: {personal_info.phone}")
                print(f"  Location: {personal_info.location}")
                print(f"  LinkedIn: {personal_info.linkedin_url}")
                print(f"  Website: {personal_info.website}")

                if errors:
                    print(f"\n⚠️ Validation warnings ({len(errors)}):")
                    for error in errors:
                        print(f"  • {error}")

                # Ask if user wants to apply to existing profile
                apply = input("\nApply this information to your profile? (y/n): ").lower().startswith('y')

                if apply:
                    # Load existing profile or create new one
                    profile = self.storage.load_profile() or UserProfile()

                    # Update personal info
                    profile.personal_info = personal_info

                    # Save updated profile
                    if self.storage.save_profile(profile):
                        print("✅ Personal information applied to profile successfully!")
                    else:
                        print("❌ Failed to save updated profile")
                else:
                    print("ℹ️ Personal information not applied")
            else:
                print(f"\n❌ Failed to parse personal information:")
                for error in errors:
                    print(f"  • {error}")

        except Exception as e:
            print(f"❌ Error importing personal information: {str(e)}")

    def create_personal_info_templates_cli(self):
        """Create personal information template files via CLI"""
        print("\n📄 Create Personal Information Templates")
        print("-" * 40)

        # Get output directory
        output_dir = input("Enter directory to save templates (Enter for current directory): ").strip()
        if not output_dir:
            output_dir = "."

        try:
            if PARSER_AVAILABLE:
                created_files = PersonalInfoParser.create_template_files(output_dir)
            else:
                # Fallback: copy template files manually
                template_files = [
                    'personal_info_template.json',
                    'personal_info_template.csv',
                    'personal_info_template.txt'
                ]

                created_files = []
                for template_file in template_files:
                    source_path = Path(template_file)
                    dest_path = Path(output_dir) / template_file

                    if source_path.exists():
                        os.makedirs(output_dir, exist_ok=True)
                        shutil.copy2(source_path, dest_path)
                        created_files.append(str(dest_path))

            if created_files:
                print(f"\n✅ Template files created in: {os.path.abspath(output_dir)}")
                for file_path in created_files:
                    print(f"  • {os.path.basename(file_path)}")

                print(f"\n📋 How to use:")
                print(f"1. Choose a template file format (JSON, CSV, or TXT)")
                print(f"2. Fill in your personal information")
                print(f"3. Save the file")
                print(f"4. Import using option 6 from the main menu")
            else:
                print("❌ No template files were created")
                print("Template files may not be available in the current directory")

        except Exception as e:
            print(f"❌ Error creating templates: {str(e)}")


def main():
    """Main entry point"""
    import sys
    import tkinter.simpledialog

    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        # Run CLI interface
        cli = ProfileManagerCLI()
        cli.run()
    else:
        # Run GUI interface
        try:
            gui = ProfileManagerGUI()
            gui.run()
        except tk.TclError:
            print("❌ GUI not available. Running CLI interface instead...")
            cli = ProfileManagerCLI()
            cli.run()


if __name__ == "__main__":
    main()
