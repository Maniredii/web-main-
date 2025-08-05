#!/usr/bin/env python3
"""
🚀 Consolidated LinkedIn Automation with Ollama Intelligence
Complete LinkedIn job application automation with AI-powered decision making
"""

import asyncio
import io
import json
import logging
import os
import random
import requests
import time
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np
from PIL import Image
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# Import profile integration
try:
    from profile_integration import AutomationProfileAdapter, FormFieldMapper
    PROFILE_INTEGRATION_AVAILABLE = True
except ImportError:
    PROFILE_INTEGRATION_AVAILABLE = False
    print("Profile integration not available - using legacy profile loading")

# Import user details loader
try:
    from user_details_loader import UserDetailsLoader
    USER_DETAILS_AVAILABLE = True
except ImportError:
    USER_DETAILS_AVAILABLE = False
    print("User details loader not available")

# Import resume optimization system
try:
    from resume_optimizer import ResumeOptimizer, OptimizationResult
    from job_description_parser import JobDescriptionParser
    from resume_parser import ResumeParser
    RESUME_OPTIMIZATION_AVAILABLE = True
except ImportError:
    RESUME_OPTIMIZATION_AVAILABLE = False
    print("Resume optimization system not available")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AutomationStrategy(Enum):
    """Automation strategies"""
    CONSERVATIVE = "conservative"
    ADAPTIVE = "adaptive" 
    AGGRESSIVE = "aggressive"


@dataclass
class JobListing:
    """Job listing information"""
    title: str
    company: str
    location: str
    url: str
    description: str = ""
    salary: str = ""
    posted_date: str = ""


@dataclass
class ApplicationResult:
    """Application result tracking"""
    job: JobListing
    success: bool
    reason: str
    ai_confidence: float = 0.0
    time_taken: float = 0.0
    resume_optimized: bool = False
    optimization_score: float = 0.0
    optimized_resume_path: str = ""


class OllamaManager:
    """Simplified Ollama integration"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:7b"):
        self.base_url = base_url
        self.model = model
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                if self.model in models:
                    logger.info(f"✅ Ollama available with model: {self.model}")
                    return True
                else:
                    logger.warning(f"⚠️ Model {self.model} not found. Available: {models}")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Ollama not available: {e}")
            return False
    
    def query(self, prompt: str, max_tokens: int = 512) -> Optional[str]:
        """Query Ollama with prompt"""
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
            logger.error(f"Ollama query error: {e}")
            return None


class LinkedInOllamaAutomation:
    """Consolidated LinkedIn automation with Ollama intelligence"""
    
    def __init__(self, profile_path: str = "user_profile.json", strategy: AutomationStrategy = AutomationStrategy.ADAPTIVE):
        load_dotenv()

        # Initialize profile system
        self.profile_adapter = None
        self.field_mapper = None
        self.user_details = None

        # Try to load user details first (new simple system)
        if USER_DETAILS_AVAILABLE:
            try:
                self.user_details = UserDetailsLoader()
                if self.user_details.is_configured():
                    logger.info("✅ Using user details configuration")
                else:
                    logger.warning("⚠️ User details not configured, falling back to profile system")
                    self.user_details = None
            except Exception as e:
                logger.warning(f"⚠️ User details loader failed: {e}")
                self.user_details = None

        # Try enhanced profile system if user details not available
        if not self.user_details and PROFILE_INTEGRATION_AVAILABLE:
            try:
                self.profile_adapter = AutomationProfileAdapter(profile_path)
                if self.profile_adapter.profile:
                    self.field_mapper = FormFieldMapper(self.profile_adapter.profile)
                    logger.info("✅ Using enhanced profile management system")
                else:
                    logger.warning("⚠️ No profile found in enhanced system, falling back to legacy")
            except Exception as e:
                logger.warning(f"⚠️ Profile adapter failed: {e}, using legacy system")

        # Load user profile (user details, enhanced, or legacy)
        if self.user_details:
            self.profile = self._convert_user_details_to_profile()
        elif self.profile_adapter:
            self.profile = self.profile_adapter.get_profile_dict()
        else:
            self.profile = self._load_profile(profile_path)

        self.strategy = strategy
        
        # Initialize Ollama
        self.ollama = OllamaManager(
            base_url=os.getenv('OLLAMA_ENDPOINT', 'http://localhost:11434'),
            model=os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')
        )
        
        # LinkedIn credentials
        self.email = self.profile['personal_info']['email']
        self.password = os.getenv('LINKEDIN_PASSWORD')
        
        # Search criteria
        search_criteria = self.profile['search_criteria']
        self.keywords = search_criteria['keywords'][0] if search_criteria['keywords'] else "Software Engineer"
        self.location = search_criteria['location']
        self.experience_level = search_criteria.get('experience_level', 'Mid-Senior level')
        
        # Automation settings
        self.max_applications = search_criteria.get('max_applications', 10)
        self.applications_sent = 0
        self.application_results: List[ApplicationResult] = []
        
        # Browser setup
        self.driver = None
        self.wait = None

        # Resume optimization setup
        self.resume_optimizer = None
        self.original_resume_path = None
        self.enable_resume_optimization = True

        if RESUME_OPTIMIZATION_AVAILABLE and self.enable_resume_optimization:
            try:
                self.resume_optimizer = ResumeOptimizer(self.ollama)
                # Get resume path from profile
                self.original_resume_path = self.profile.get('resume_path')
                if not self.original_resume_path or not os.path.exists(self.original_resume_path):
                    # Try to find sample resume in current directory
                    possible_resumes = ['sample resume.docx', 'resume.docx', 'resume.pdf', 'cv.docx', 'cv.pdf']
                    for resume_file in possible_resumes:
                        if os.path.exists(resume_file):
                            self.original_resume_path = resume_file
                            logger.info(f"📄 Found resume file: {resume_file}")
                            break

                if self.original_resume_path:
                    logger.info(f"✅ Resume optimization enabled with: {self.original_resume_path}")
                else:
                    logger.warning("⚠️ No resume file found - resume optimization disabled")
                    self.enable_resume_optimization = False

            except Exception as e:
                logger.warning(f"⚠️ Resume optimization setup failed: {e}")
                self.enable_resume_optimization = False
        else:
            logger.info("📄 Resume optimization not available or disabled")
    
    def _convert_user_details_to_profile(self) -> Dict[str, Any]:
        """Convert user details to profile format"""
        personal = self.user_details.get_personal_info()
        professional = self.user_details.get_professional_info()
        job_prefs = self.user_details.get_job_preferences()
        app_settings = self.user_details.get_application_settings()

        # Convert to legacy profile format
        profile = {
            'personal_info': {
                'name': personal.get('name', ''),
                'email': personal.get('email', ''),
                'phone': personal.get('phone', ''),
                'location': personal.get('location', ''),
                'linkedin_url': personal.get('linkedin_url', ''),
                'website': personal.get('website', '')
            },
            'professional_info': {
                'current_title': professional.get('current_title', ''),
                'experience_years': professional.get('experience_years', 0),
                'skills': professional.get('skills', []),
                'summary': professional.get('summary', ''),
                'education': professional.get('education', ''),
                'certifications': professional.get('certifications', [])
            },
            'search_criteria': {
                'keywords': job_prefs.get('desired_roles', ['Software Engineer']),
                'location': personal.get('location', ''),
                'experience_level': job_prefs.get('experience_level', 'Mid-Senior level'),
                'job_type': job_prefs.get('work_type', 'Full-time'),
                'remote': job_prefs.get('remote_preference', 'Hybrid')
            },
            'application_settings': {
                'max_applications_per_day': app_settings.get('max_applications_per_day', 10),
                'auto_apply_easy_apply_only': app_settings.get('auto_apply_easy_apply_only', True),
                'skip_companies': app_settings.get('skip_companies', []),
                'preferred_companies': app_settings.get('preferred_companies', [])
            }
        }

        logger.info("✅ User details converted to profile format")
        return profile

    def _load_profile(self, profile_path: str) -> Dict[str, Any]:
        """Load user profile from JSON file"""
        try:
            with open(profile_path, 'r') as f:
                profile = json.load(f)
            logger.info("✅ User profile loaded successfully")
            return profile
        except FileNotFoundError:
            logger.error(f"❌ Profile file {profile_path} not found!")
            raise
        except json.JSONDecodeError:
            logger.error(f"❌ Invalid JSON in {profile_path}!")
            raise
    
    def setup_browser(self):
        """Setup Chrome browser with advanced stealth options"""
        chrome_options = Options()
        
        # Basic stealth options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Advanced anti-detection measures
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Faster loading, less bot-like
        chrome_options.add_argument("--disable-javascript")  # Will be re-enabled after setup
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        
        # Random user agent rotation
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        # Window size randomization
        window_sizes = [(1920, 1080), (1366, 768), (1440, 900), (1536, 864), (1280, 720)]
        window_size = random.choice(window_sizes)
        chrome_options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
        
        # Additional preferences
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "geolocation": 2,
                "media_stream": 2
            },
            "profile.managed_default_content_settings": {
                "images": 2
            },
            "profile.default_content_settings": {
                "popups": 0
            }
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute stealth scripts
        self._apply_stealth_scripts()
        
        # Set random viewport
        self.driver.set_window_size(window_size[0], window_size[1])
        
        # Add random mouse movements and scrolling behavior
        self._simulate_human_behavior()
        
        self.wait = WebDriverWait(self.driver, 10)
        
        logger.info("✅ Advanced stealth browser setup complete")
    
    def _apply_stealth_scripts(self):
        """Apply additional stealth scripts to avoid detection"""
        stealth_scripts = [
            # Override permissions
            "Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})})",
            
            # Override plugins
            "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})",
            
            # Override languages
            "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})",
            
            # Override platform
            "Object.defineProperty(navigator, 'platform', {get: () => 'Win32'})",
            
            # Override hardware concurrency
            "Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8})",
            
            # Override device memory
            "Object.defineProperty(navigator, 'deviceMemory', {get: () => 8})",
            
            # Override connection
            "Object.defineProperty(navigator, 'connection', {get: () => ({effectiveType: '4g', rtt: 50, downlink: 10})})",
            
            # Override chrome runtime
            "Object.defineProperty(window, 'chrome', {get: () => ({runtime: {}}), configurable: true})",
            
            # Override automation properties
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array",
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise",
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol",
            
            # Override automation functions
            "window.navigator.chrome = {runtime: {}}"
        ]
        
        for script in stealth_scripts:
            try:
                self.driver.execute_script(script)
            except Exception as e:
                logger.debug(f"Stealth script failed: {e}")
        
        # Handle webdriver property separately to avoid conflicts
        try:
            # Try to remove webdriver property if it exists
            self.driver.execute_script("delete navigator.webdriver")
        except:
            pass
        
        try:
            # Set webdriver to undefined if possible
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined, configurable: true})")
        except:
            pass
    
    def _simulate_human_behavior(self):
        """Simulate human-like behavior patterns"""
        try:
            # Random mouse movements
            for _ in range(random.randint(3, 8)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                self.driver.execute_script(f"document.elementFromPoint({x}, {y})")
                time.sleep(random.uniform(0.1, 0.5))
            
            # Random scrolling
            scroll_amount = random.randint(100, 500)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
            time.sleep(random.uniform(0.5, 1.5))
            
            # Random scroll back
            self.driver.execute_script(f"window.scrollBy(0, -{scroll_amount//2})")
            time.sleep(random.uniform(0.3, 0.8))
            
        except Exception as e:
            logger.debug(f"Human behavior simulation failed: {e}")
    
    def _add_random_delays(self, min_delay=1, max_delay=3):
        """Add random delays to simulate human behavior"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _human_like_typing(self, element, text):
        """Simulate human-like typing with random delays"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # Random typing speed
    
    def login_to_linkedin(self) -> bool:
        """Login to LinkedIn with advanced anti-detection measures"""
        try:
            logger.info("🔐 Logging into LinkedIn with stealth mode...")
            
            # Add random delay before accessing LinkedIn
            self._add_random_delays(2, 5)
            
            # Navigate to LinkedIn with random delays
            self.driver.get("https://www.linkedin.com")
            self._add_random_delays(3, 6)
            
            # Navigate to login page
            self.driver.get("https://www.linkedin.com/login")
            self._add_random_delays(2, 4)
            
            # Simulate human behavior before login
            self._simulate_human_behavior()
            
            # Wait for login form with multiple selectors
            email_field = None
            password_field = None
            
            # Try multiple selectors for email field
            email_selectors = [
                (By.ID, "username"),
                (By.NAME, "session_key"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.XPATH, "//input[@type='email']")
            ]
            
            for selector in email_selectors:
                try:
                    email_field = self.wait.until(EC.presence_of_element_located(selector))
                    break
                except:
                    continue
            
            if not email_field:
                logger.error("❌ Could not find email field")
                return False
            
            # Try multiple selectors for password field
            password_selectors = [
                (By.ID, "password"),
                (By.NAME, "session_password"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.XPATH, "//input[@type='password']")
            ]
            
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(*selector)
                    break
                except:
                    continue
            
            if not password_field:
                logger.error("❌ Could not find password field")
                return False
            
            # Human-like typing for email
            logger.info("📧 Entering email...")
            self._human_like_typing(email_field, self.email)
            self._add_random_delays(1, 3)
            
            # Human-like typing for password
            logger.info("🔑 Entering password...")
            self._human_like_typing(password_field, self.password)
            self._add_random_delays(1, 3)
            
            # Find and click login button with multiple selectors
            login_button = None
            login_selectors = [
                (By.XPATH, "//button[@type='submit']"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Sign in')]"),
                (By.XPATH, "//button[contains(text(), 'Sign In')]"),
                (By.CSS_SELECTOR, ".btn__primary--large")
            ]
            
            for selector in login_selectors:
                try:
                    login_button = self.driver.find_element(*selector)
                    break
                except:
                    continue
            
            if not login_button:
                logger.error("❌ Could not find login button")
                return False
            
            # Simulate human behavior before clicking
            self._simulate_human_behavior()
            
            # Click login button
            logger.info("🖱️ Clicking login button...")
            login_button.click()
            
            # Wait for login with progressive delays
            self._add_random_delays(3, 6)
            
            # Check for various security challenges
            security_indicators = [
                "challenge",
                "checkpoint", 
                "security",
                "verification",
                "captcha",
                "phone",
                "email-verification"
            ]
            
            current_url = self.driver.current_url.lower()
            if any(indicator in current_url for indicator in security_indicators):
                logger.warning("⚠️ Security challenge detected - manual intervention required")
                self._handle_manual_intervention("Please complete the security challenge and press OK")
                self._add_random_delays(5, 10)
            
            # Check for 2FA if present
            try:
                two_fa_elements = self.driver.find_elements(By.XPATH, "//input[@type='text' and contains(@placeholder, 'code') or contains(@placeholder, 'Code')]")
                if two_fa_elements:
                    logger.warning("⚠️ 2FA detected - manual intervention required")
                    self._handle_manual_intervention("Please enter your 2FA code and press OK")
                    self._add_random_delays(3, 6)
            except:
                pass
            
            # Verify login success with multiple indicators
            success_indicators = [
                "feed" in self.driver.current_url,
                "mynetwork" in self.driver.current_url,
                "messaging" in self.driver.current_url,
                "jobs" in self.driver.current_url
            ]
            
            # Also check for profile elements
            try:
                profile_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-control-name='identity_welcome_message']")
                if profile_elements:
                    success_indicators.append(True)
            except:
                pass
            
            if any(success_indicators):
                logger.info("✅ Successfully logged into LinkedIn")
                # Simulate normal user behavior after login
                self._simulate_post_login_behavior()
                return True
            else:
                logger.error("❌ Login failed - could not verify successful login")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    def _simulate_post_login_behavior(self):
        """Simulate normal user behavior after login"""
        try:
            # Random scrolling
            for _ in range(random.randint(2, 5)):
                scroll_amount = random.randint(200, 800)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
                self._add_random_delays(1, 3)
            
            # Random mouse movements
            for _ in range(random.randint(3, 7)):
                x = random.randint(100, 900)
                y = random.randint(100, 700)
                self.driver.execute_script(f"document.elementFromPoint({x}, {y})")
                self._add_random_delays(0.5, 1.5)
            
            # Sometimes click on profile or other elements
            if random.random() < 0.3:
                try:
                    profile_link = self.driver.find_element(By.CSS_SELECTOR, "[data-control-name='identity_welcome_message']")
                    profile_link.click()
                    self._add_random_delays(2, 4)
                    self.driver.back()
                    self._add_random_delays(1, 3)
                except:
                    pass
                    
        except Exception as e:
            logger.debug(f"Post-login behavior simulation failed: {e}")
    
    def _simulate_job_reading_behavior(self):
        """Simulate human-like job reading behavior"""
        try:
            # Scroll through job description
            for _ in range(random.randint(3, 8)):
                scroll_amount = random.randint(100, 400)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
                self._add_random_delays(1, 3)
            
            # Sometimes scroll back up
            if random.random() < 0.4:
                self.driver.execute_script("window.scrollTo(0, 0)")
                self._add_random_delays(1, 2)
            
            # Random mouse movements over job content
            for _ in range(random.randint(2, 5)):
                x = random.randint(200, 800)
                y = random.randint(200, 600)
                self.driver.execute_script(f"document.elementFromPoint({x}, {y})")
                self._add_random_delays(0.5, 1.5)
            
            # Sometimes highlight text (simulate selection)
            if random.random() < 0.3:
                try:
                    job_elements = self.driver.find_elements(By.CSS_SELECTOR, ".job-description, .description__text")
                    if job_elements:
                        element = random.choice(job_elements)
                        self.driver.execute_script("arguments[0].style.backgroundColor = 'yellow'", element)
                        self._add_random_delays(1, 2)
                        self.driver.execute_script("arguments[0].style.backgroundColor = ''", element)
                except:
                    pass
                    
        except Exception as e:
            logger.debug(f"Job reading behavior simulation failed: {e}")
    
    def _simulate_post_application_behavior(self):
        """Simulate behavior after submitting application"""
        try:
            # Wait a bit after submission
            self._add_random_delays(2, 4)
            
            # Sometimes go back to job search
            if random.random() < 0.6:
                self.driver.back()
                self._add_random_delays(1, 3)
            
            # Sometimes refresh the page
            if random.random() < 0.2:
                self.driver.refresh()
                self._add_random_delays(2, 4)
            
            # Random scrolling
            for _ in range(random.randint(1, 3)):
                scroll_amount = random.randint(100, 300)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
                self._add_random_delays(0.5, 1.5)
                
        except Exception as e:
            logger.debug(f"Post-application behavior simulation failed: {e}")
    
    def analyze_job_with_ollama(self, job: JobListing) -> Dict[str, Any]:
        """Use Ollama to analyze job compatibility"""
        if not self.ollama.available:
            return self._fallback_job_analysis(job)
        
        prompt = f"""
        Analyze this job for compatibility with the candidate profile.
        
        Job: {job.title} at {job.company}
        Location: {job.location}
        Description: {job.description[:500]}
        
        Candidate Skills: {', '.join(self.profile.get('skills', []))}
        Experience: {self.profile.get('experience_years', 0)} years
        Preferences: Remote OK: {self.profile.get('remote_preference', True)}
        
        Respond with JSON only:
        {{"compatibility_score": 0.85, "should_apply": true, "reasoning": "Strong skill match"}}
        """
        
        response = self.ollama.query(prompt, max_tokens=256)
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                logger.warning("Failed to parse Ollama job analysis")
        
        return self._fallback_job_analysis(job)
    
    def _fallback_job_analysis(self, job: JobListing) -> Dict[str, Any]:
        """Fallback job analysis without AI"""
        user_skills = set(skill.lower() for skill in self.profile.get('skills', []))
        job_text = f"{job.title} {job.description}".lower()
        
        skill_matches = [skill for skill in user_skills if skill in job_text]
        compatibility_score = min(len(skill_matches) / max(len(user_skills), 1), 1.0)
        
        return {
            "compatibility_score": compatibility_score,
            "should_apply": compatibility_score > 0.3,
            "reasoning": f"Keyword analysis: {len(skill_matches)} skills matched"
        }
    
    def generate_cover_letter_with_ollama(self, job: JobListing) -> str:
        """Generate cover letter using Ollama"""
        if not self.ollama.available:
            return self._fallback_cover_letter(job)
        
        prompt = f"""
        Write a professional cover letter for this job application.
        
        Job: {job.title} at {job.company}
        Candidate: {self.profile['personal_info']['name']}
        Skills: {', '.join(self.profile.get('skills', [])[:5])}
        Experience: {self.profile.get('experience_years', 0)} years
        
        Requirements:
        - Professional tone
        - 3 paragraphs maximum
        - Highlight relevant skills
        - Show enthusiasm
        
        Write only the cover letter content.
        """
        
        response = self.ollama.query(prompt, max_tokens=400)
        if response:
            return response.strip()
        
        return self._fallback_cover_letter(job)
    
    def _fallback_cover_letter(self, job: JobListing) -> str:
        """Fallback cover letter without AI"""
        return f"""Dear Hiring Manager,

I am writing to express my interest in the {job.title} position at {job.company}. With {self.profile.get('experience_years', 0)} years of experience and expertise in {', '.join(self.profile.get('skills', [])[:3])}, I am confident I would be a valuable addition to your team.

My background aligns well with your requirements, and I am particularly excited about the opportunity to contribute to {job.company}'s mission and grow my career in this role.

I would welcome the opportunity to discuss how my experience can benefit your team. Thank you for considering my application.

Best regards,
{self.profile['personal_info']['name']}"""

    def search_jobs(self) -> List[JobListing]:
        """Search for jobs on LinkedIn"""
        try:
            logger.info(f"🔍 Searching for jobs: {self.keywords} in {self.location}")

            # Navigate to jobs page
            jobs_url = f"https://www.linkedin.com/jobs/search/?keywords={self.keywords}&location={self.location}&f_E={self._get_experience_filter()}&f_TPR=r86400"
            self.driver.get(jobs_url)
            time.sleep(3)

            jobs = []
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job-search-card")

            for card in job_cards[:20]:  # Limit to first 20 jobs
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, ".base-search-card__title")
                    company_elem = card.find_element(By.CSS_SELECTOR, ".base-search-card__subtitle")
                    location_elem = card.find_element(By.CSS_SELECTOR, ".job-search-card__location")
                    link_elem = card.find_element(By.CSS_SELECTOR, ".base-card__full-link")

                    job = JobListing(
                        title=title_elem.text.strip(),
                        company=company_elem.text.strip(),
                        location=location_elem.text.strip(),
                        url=link_elem.get_attribute("href")
                    )
                    jobs.append(job)

                except Exception as e:
                    logger.warning(f"⚠️ Error parsing job card: {e}")
                    continue

            logger.info(f"✅ Found {len(jobs)} jobs")
            return jobs

        except Exception as e:
            logger.error(f"❌ Job search error: {e}")
            return []

    def _get_experience_filter(self) -> str:
        """Get LinkedIn experience level filter"""
        experience_map = {
            "Internship": "1",
            "Entry level": "2",
            "Associate": "3",
            "Mid-Senior level": "4",
            "Director": "5",
            "Executive": "6"
        }
        return experience_map.get(self.experience_level, "4")

    def apply_to_job(self, job: JobListing) -> ApplicationResult:
        """Apply to a single job with advanced anti-detection measures"""
        start_time = time.time()

        try:
            logger.info(f"📝 Applying to: {job.title} at {job.company}")

            # Add random delay before starting application
            self._add_random_delays(2, 5)

            # Analyze job compatibility
            analysis = self.analyze_job_with_ollama(job)

            if not analysis['should_apply']:
                return ApplicationResult(
                    job=job,
                    success=False,
                    reason=f"Job not suitable: {analysis['reasoning']}",
                    ai_confidence=analysis['compatibility_score'],
                    time_taken=time.time() - start_time
                )

            # Navigate to job page with human-like behavior
            self.driver.get(job.url)
            self._add_random_delays(3, 6)
            
            # Simulate reading the job description
            self._simulate_job_reading_behavior()

            # Get job description for better analysis
            try:
                description_elem = self.driver.find_element(By.CSS_SELECTOR, ".show-more-less-html__markup")
                job.description = description_elem.text[:1000]  # Limit description length
            except:
                pass

            # Optimize resume for this specific job
            optimized_resume_path = None
            optimization_score = 0.0
            resume_optimized = False

            if self.enable_resume_optimization and self.original_resume_path and job.description:
                try:
                    logger.info("🔧 Optimizing resume for job requirements...")
                    optimization_result = self.resume_optimizer.optimize_resume_for_job(
                        self.original_resume_path,
                        job.description,
                        job.title,
                        job.company
                    )

                    if optimization_result:
                        optimized_resume_path = optimization_result.output_file_path
                        optimization_score = optimization_result.optimization_score
                        resume_optimized = True

                        # Update profile to use optimized resume for this application
                        if os.path.exists(optimized_resume_path):
                            self.profile['resume_path'] = optimized_resume_path
                            logger.info(f"✅ Resume optimized with score: {optimization_score:.2f}")
                        else:
                            logger.warning("⚠️ Optimized resume file not found, using original")
                    else:
                        logger.warning("⚠️ Resume optimization failed, using original resume")

                except Exception as e:
                    logger.warning(f"⚠️ Resume optimization error: {e}")
                    # Continue with original resume

            # Find and click Easy Apply button
            if not self._click_easy_apply():
                return ApplicationResult(
                    job=job,
                    success=False,
                    reason="Easy Apply button not found",
                    ai_confidence=0.0,
                    time_taken=time.time() - start_time,
                    resume_optimized=resume_optimized,
                    optimization_score=optimization_score,
                    optimized_resume_path=optimized_resume_path or ""
                )

            # Fill application form
            if not self._fill_application_form(job):
                return ApplicationResult(
                    job=job,
                    success=False,
                    reason="Failed to fill application form",
                    ai_confidence=analysis['compatibility_score'],
                    time_taken=time.time() - start_time,
                    resume_optimized=resume_optimized,
                    optimization_score=optimization_score,
                    optimized_resume_path=optimized_resume_path or ""
                )

            # Submit application
            if self._submit_application():
                self.applications_sent += 1
                logger.info(f"✅ Successfully applied to {job.title}")
                if resume_optimized:
                    logger.info(f"📄 Used optimized resume with score: {optimization_score:.2f}")
                return ApplicationResult(
                    job=job,
                    success=True,
                    reason="Application submitted successfully",
                    ai_confidence=analysis['compatibility_score'],
                    time_taken=time.time() - start_time,
                    resume_optimized=resume_optimized,
                    optimization_score=optimization_score,
                    optimized_resume_path=optimized_resume_path or ""
                )
            else:
                return ApplicationResult(
                    job=job,
                    success=False,
                    reason="Failed to submit application",
                    ai_confidence=analysis['compatibility_score'],
                    time_taken=time.time() - start_time,
                    resume_optimized=resume_optimized,
                    optimization_score=optimization_score,
                    optimized_resume_path=optimized_resume_path or ""
                )

        except Exception as e:
            logger.error(f"❌ Application error for {job.title}: {e}")
            return ApplicationResult(
                job=job,
                success=False,
                reason=f"Exception: {str(e)}",
                ai_confidence=0.0,
                time_taken=time.time() - start_time,
                resume_optimized=False,
                optimization_score=0.0,
                optimized_resume_path=""
            )

    def _click_easy_apply(self) -> bool:
        """Find and click Easy Apply button using multiple strategies"""
        try:
            # Strategy 1: Standard Easy Apply button
            easy_apply_selectors = [
                "button[aria-label*='Easy Apply']",
                "button:contains('Easy Apply')",
                ".jobs-apply-button--top-card button",
                ".jobs-s-apply button"
            ]

            for selector in easy_apply_selectors:
                try:
                    if "contains" in selector:
                        # Use XPath for text-based selection
                        xpath = f"//button[contains(text(), 'Easy Apply')]"
                        button = self.driver.find_element(By.XPATH, xpath)
                    else:
                        button = self.driver.find_element(By.CSS_SELECTOR, selector)

                    if button.is_enabled():
                        button.click()
                        time.sleep(2)
                        return True
                except:
                    continue

            # Strategy 2: Computer vision approach
            if self._find_easy_apply_with_cv():
                return True

            logger.warning("⚠️ Easy Apply button not found")
            return False

        except Exception as e:
            logger.error(f"❌ Error clicking Easy Apply: {e}")
            return False

    def _find_easy_apply_with_cv(self) -> bool:
        """Use computer vision to find Easy Apply button"""
        try:
            # Take screenshot
            screenshot = self.driver.get_screenshot_as_png()
            image = Image.open(io.BytesIO(screenshot))
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Template matching for "Easy Apply" text
            # This is a simplified approach - in practice you'd need template images
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

            # Look for button-like rectangles
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if 80 < w < 200 and 30 < h < 60:  # Button-like dimensions
                    # Click in the center of the potential button
                    center_x = x + w // 2
                    center_y = y + h // 2

                    # Convert to Selenium click
                    self.driver.execute_script(f"document.elementFromPoint({center_x}, {center_y}).click();")
                    time.sleep(2)

                    # Check if application modal opened
                    if self._is_application_modal_open():
                        return True

            return False

        except Exception as e:
            logger.warning(f"⚠️ Computer vision approach failed: {e}")
            return False

    def _is_application_modal_open(self) -> bool:
        """Check if application modal is open"""
        try:
            modal_selectors = [
                ".jobs-easy-apply-modal",
                "[data-test-modal]",
                ".artdeco-modal"
            ]

            for selector in modal_selectors:
                if self.driver.find_elements(By.CSS_SELECTOR, selector):
                    return True
            return False
        except:
            return False

    def _fill_application_form(self, job: JobListing) -> bool:
        """Fill application form with advanced anti-detection measures"""
        try:
            # Wait for form to load with random delay
            self._add_random_delays(2, 4)

            # Handle multiple form pages
            max_pages = 5
            current_page = 0

            while current_page < max_pages:
                current_page += 1
                logger.info(f"📝 Filling form page {current_page}")

                # Simulate human behavior before filling each page
                self._simulate_human_behavior()

                # Fill current page
                if not self._fill_current_form_page(job):
                    logger.warning(f"⚠️ Failed to fill form page {current_page}")

                # Add random delay after filling page
                self._add_random_delays(1, 3)

                # Check for next button
                next_button = self._find_next_button()
                if next_button:
                    # Simulate human behavior before clicking next
                    self._simulate_human_behavior()
                    next_button.click()
                    self._add_random_delays(2, 4)
                else:
                    # No next button, we're on the last page
                    break

            return True

        except Exception as e:
            logger.error(f"❌ Form filling error: {e}")
            return False

    def _fill_current_form_page(self, job: JobListing) -> bool:
        """Fill current form page"""
        try:
            # Find all form fields
            form_fields = self.driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")

            for field in form_fields:
                try:
                    field_type = field.get_attribute("type")
                    field_name = field.get_attribute("name") or field.get_attribute("id") or ""
                    field_label = self._get_field_label(field)

                    if field_type in ["text", "email", "tel"] or field.tag_name == "textarea":
                        value = self._get_field_value(field_name, field_label, field_type)
                        if value:
                            # Use human-like typing instead of direct send_keys
                            self._human_like_typing(field, value)
                            self._add_random_delays(0.5, 1.5)

                    elif field.tag_name == "select":
                        self._handle_select_field(field, field_name, field_label)

                    elif field_type == "file":
                        self._handle_file_upload(field, field_name, field_label)

                except Exception as e:
                    logger.warning(f"⚠️ Error filling field: {e}")
                    continue

            return True

        except Exception as e:
            logger.error(f"❌ Error filling current page: {e}")
            return False

    def _get_field_label(self, field) -> str:
        """Get field label text"""
        try:
            # Try to find associated label
            field_id = field.get_attribute("id")
            if field_id:
                label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{field_id}']")
                return label.text.strip()
        except:
            pass

        try:
            # Try parent element
            parent = field.find_element(By.XPATH, "..")
            label = parent.find_element(By.CSS_SELECTOR, "label")
            return label.text.strip()
        except:
            pass

        return ""

    def _get_field_value(self, field_name: str, field_label: str, field_type: str) -> str:
        """Get appropriate value for form field"""
        # Use user details system if available (highest priority)
        if self.user_details:
            field_text = f"{field_name} {field_label}".lower()

            # Try direct field mapping first
            for field_key in [field_name.lower(), field_label.lower().replace(' ', '_')]:
                value = self.user_details.get_field_value(field_key)
                if value:
                    return value

            # Try pattern matching
            if any(term in field_text for term in ['first', 'fname', 'given']):
                return self.user_details.get_field_value('first_name')
            elif any(term in field_text for term in ['last', 'lname', 'surname']):
                return self.user_details.get_field_value('last_name')
            elif any(term in field_text for term in ['email', 'mail']):
                return self.user_details.get_field_value('email')
            elif any(term in field_text for term in ['phone', 'tel', 'mobile']):
                return self.user_details.get_field_value('phone')
            elif any(term in field_text for term in ['location', 'city', 'address']):
                return self.user_details.get_field_value('location')
            elif any(term in field_text for term in ['linkedin']):
                return self.user_details.get_field_value('linkedin')
            elif any(term in field_text for term in ['website', 'portfolio']):
                return self.user_details.get_field_value('website')
            elif any(term in field_text for term in ['title', 'position', 'role']):
                return self.user_details.get_field_value('current_title')
            elif any(term in field_text for term in ['experience', 'years']):
                return str(self.user_details.get_field_value('experience'))
            elif any(term in field_text for term in ['education', 'degree']):
                return self.user_details.get_field_value('education')
            elif any(term in field_text for term in ['summary', 'about']):
                return self.user_details.get_field_value('summary')

        # Use enhanced profile system if available
        elif self.field_mapper:
            value = self.field_mapper.get_field_value(field_name, field_label)
            if value:
                return value

        # Fallback to legacy system
        field_text = f"{field_name} {field_label}".lower()

        # Personal information
        if any(term in field_text for term in ['first', 'fname', 'given']):
            return self.profile['personal_info']['name'].split()[0]
        elif any(term in field_text for term in ['last', 'lname', 'surname']):
            return self.profile['personal_info']['name'].split()[-1]
        elif any(term in field_text for term in ['email', 'mail']):
            return self.profile['personal_info']['email']
        elif any(term in field_text for term in ['phone', 'tel', 'mobile']):
            return self.profile['personal_info'].get('phone', '')

        # Professional information
        elif any(term in field_text for term in ['experience', 'years']):
            return str(self.profile.get('experience_years', 0))
        elif any(term in field_text for term in ['salary', 'compensation']):
            return str(self.profile.get('desired_salary', ''))
        elif any(term in field_text for term in ['cover', 'letter', 'why']):
            return self.generate_cover_letter_with_ollama(job) if hasattr(self, 'job') else ""

        # Location
        elif any(term in field_text for term in ['location', 'city', 'address']):
            return self.profile['personal_info'].get('location', '')

        return ""

    def _handle_select_field(self, field, field_name: str, field_label: str):
        """Handle select dropdown fields"""
        try:
            select = Select(field)
            field_text = f"{field_name} {field_label}".lower()

            # Get all options
            options = [option.text.strip() for option in select.options if option.text.strip()]

            # Experience level selection
            if any(term in field_text for term in ['experience', 'level', 'years']):
                target_years = self.profile.get('experience_years', 0)
                if target_years < 1:
                    select.select_by_visible_text("Less than 1 year")
                elif target_years < 3:
                    select.select_by_visible_text("1-2 years")
                elif target_years < 5:
                    select.select_by_visible_text("3-5 years")
                else:
                    select.select_by_visible_text("5+ years")

            # Education level
            elif any(term in field_text for term in ['education', 'degree']):
                education = self.profile.get('education', '').lower()
                if 'master' in education or 'mba' in education:
                    select.select_by_visible_text("Master's degree")
                elif 'bachelor' in education or 'bs' in education:
                    select.select_by_visible_text("Bachelor's degree")
                else:
                    select.select_by_index(1)  # Select first non-empty option

            # Default: select first non-empty option
            else:
                if len(options) > 1:
                    select.select_by_index(1)

        except Exception as e:
            logger.warning(f"⚠️ Error handling select field: {e}")

    def _handle_file_upload(self, field, field_name: str, field_label: str):
        """Handle file upload fields with optimized resume support"""
        try:
            field_text = f"{field_name} {field_label}".lower()

            if any(term in field_text for term in ['resume', 'cv']):
                # Use optimized resume if available, otherwise use original
                resume_path = self.profile.get('resume_path')
                if resume_path and os.path.exists(resume_path):
                    field.send_keys(os.path.abspath(resume_path))
                    logger.info(f"📄 Uploaded resume: {os.path.basename(resume_path)}")
                    time.sleep(1)
                else:
                    logger.warning("⚠️ No resume file found for upload")
            elif any(term in field_text for term in ['cover', 'letter']):
                cover_letter_path = self.profile.get('cover_letter_path')
                if cover_letter_path and os.path.exists(cover_letter_path):
                    field.send_keys(os.path.abspath(cover_letter_path))
                    time.sleep(1)

        except Exception as e:
            logger.warning(f"⚠️ Error handling file upload: {e}")

    def _find_next_button(self):
        """Find next button in application form"""
        next_selectors = [
            "button[aria-label*='Continue']",
            "button[aria-label*='Next']",
            "button:contains('Next')",
            "button:contains('Continue')",
            ".artdeco-button--primary"
        ]

        for selector in next_selectors:
            try:
                if "contains" in selector:
                    xpath = selector.replace("button:contains('", "//button[contains(text(), '").replace("')", "')]")
                    button = self.driver.find_element(By.XPATH, xpath)
                else:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)

                if button.is_enabled() and button.is_displayed():
                    return button
            except:
                continue

        return None

    def _submit_application(self) -> bool:
        """Submit the application"""
        try:
            submit_selectors = [
                "button[aria-label*='Submit']",
                "button:contains('Submit')",
                "button:contains('Send application')",
                ".jobs-apply-form__submit-button"
            ]

            for selector in submit_selectors:
                try:
                    if "contains" in selector:
                        xpath = selector.replace("button:contains('", "//button[contains(text(), '").replace("')", "')]")
                        button = self.driver.find_element(By.XPATH, xpath)
                    else:
                        button = self.driver.find_element(By.CSS_SELECTOR, selector)

                    if button.is_enabled():
                        button.click()
                        time.sleep(3)
                        return True
                except:
                    continue

            logger.warning("⚠️ Submit button not found")
            return False

        except Exception as e:
            logger.error(f"❌ Submit error: {e}")
            return False

    def _handle_manual_intervention(self, message: str):
        """Handle manual intervention requests"""
        try:
            root = tk.Tk()
            root.withdraw()  # Hide main window
            messagebox.showinfo("Manual Intervention Required", message)
            root.destroy()
        except Exception as e:
            logger.warning(f"⚠️ Manual intervention UI error: {e}")
            input(f"{message} - Press Enter to continue...")

    def run_automation(self):
        """Main automation loop"""
        try:
            logger.info("🚀 Starting LinkedIn Ollama Automation")

            # Setup browser
            self.setup_browser()

            # Login to LinkedIn
            if not self.login_to_linkedin():
                logger.error("❌ Failed to login to LinkedIn")
                return

            # Search for jobs
            jobs = self.search_jobs()
            if not jobs:
                logger.error("❌ No jobs found")
                return

            logger.info(f"📋 Found {len(jobs)} jobs to process")

            # Apply to jobs
            for i, job in enumerate(jobs):
                if self.applications_sent >= self.max_applications:
                    logger.info(f"✅ Reached maximum applications limit ({self.max_applications})")
                    break

                logger.info(f"📝 Processing job {i+1}/{len(jobs)}: {job.title}")

                # Apply to job
                result = self.apply_to_job(job)
                self.application_results.append(result)

                if result.success:
                    logger.info(f"✅ Application {self.applications_sent} successful")
                else:
                    logger.warning(f"⚠️ Application failed: {result.reason}")

                # Random delay between applications
                delay = random.uniform(30, 60)
                logger.info(f"⏳ Waiting {delay:.1f} seconds before next application...")
                time.sleep(delay)

            # Generate summary report
            self._generate_summary_report()

        except KeyboardInterrupt:
            logger.info("⏹️ Automation stopped by user")
        except Exception as e:
            logger.error(f"❌ Automation error: {e}")
        finally:
            self._cleanup()

    def _generate_summary_report(self):
        """Generate automation summary report with resume optimization stats"""
        try:
            successful_applications = [r for r in self.application_results if r.success]
            failed_applications = [r for r in self.application_results if not r.success]
            optimized_applications = [r for r in self.application_results if r.resume_optimized]

            logger.info("📊 AUTOMATION SUMMARY")
            logger.info("=" * 50)
            logger.info(f"Total jobs processed: {len(self.application_results)}")
            logger.info(f"Successful applications: {len(successful_applications)}")
            logger.info(f"Failed applications: {len(failed_applications)}")
            logger.info(f"Success rate: {len(successful_applications)/len(self.application_results)*100:.1f}%")

            # Resume optimization stats
            if self.enable_resume_optimization:
                logger.info(f"Resumes optimized: {len(optimized_applications)}")
                if optimized_applications:
                    avg_optimization_score = sum(r.optimization_score for r in optimized_applications) / len(optimized_applications)
                    logger.info(f"Average optimization score: {avg_optimization_score:.2f}")

            if self.ollama.available:
                avg_confidence = sum(r.ai_confidence for r in successful_applications) / len(successful_applications) if successful_applications else 0
                logger.info(f"Average AI confidence: {avg_confidence:.2f}")

            # Save detailed report
            report_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "summary": {
                    "total_processed": len(self.application_results),
                    "successful": len(successful_applications),
                    "failed": len(failed_applications),
                    "success_rate": len(successful_applications)/len(self.application_results)*100 if self.application_results else 0
                },
                "applications": [
                    {
                        "job_title": r.job.title,
                        "company": r.job.company,
                        "success": r.success,
                        "reason": r.reason,
                        "ai_confidence": r.ai_confidence,
                        "time_taken": r.time_taken,
                        "resume_optimized": r.resume_optimized,
                        "optimization_score": r.optimization_score,
                        "optimized_resume_path": r.optimized_resume_path
                    }
                    for r in self.application_results
                ]
            }

            report_filename = f"job_applications_{time.strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_filename, 'w') as f:
                json.dump(report_data, f, indent=2)

            logger.info(f"📄 Detailed report saved to: {report_filename}")

        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")

    def _cleanup(self):
        """Cleanup resources"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("🧹 Browser cleanup complete")
        except Exception as e:
            logger.warning(f"⚠️ Cleanup error: {e}")


def main():
    """Main entry point"""
    try:
        # Initialize automation
        automation = LinkedInOllamaAutomation(
            profile_path="user_profile.json",
            strategy=AutomationStrategy.ADAPTIVE
        )

        # Run automation
        automation.run_automation()

    except Exception as e:
        logger.error(f"❌ Main error: {e}")


if __name__ == "__main__":
    main()
