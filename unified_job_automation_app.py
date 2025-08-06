#!/usr/bin/env python3
"""
🚀 Unified Job Automation Application
Combines all features into a single Flask application with modern web interface
"""

import os
import json
import time
import random
import logging
import requests
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask app initialization
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Global state
class AppState:
    def __init__(self):
        self.is_running = False
        self.current_platform = None
        self.jobs_found = 0
        self.applications_sent = 0
        self.errors = []
        self.logs = []
        self.browser = None
        self.analyzer = None
        self.config = {}
        self.user_profile = {}

app_state = AppState()

# Enums and Data Classes
class AutomationStrategy(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

class PlatformType(Enum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    GLASSDOOR = "glassdoor"

@dataclass
class JobData:
    title: str
    company: str
    location: str
    description: str
    url: str
    platform: str
    posted_date: str
    salary: Optional[str] = None
    job_type: Optional[str] = None

@dataclass
class ApplicationResult:
    job_title: str
    company: str
    platform: str
    status: str
    timestamp: str
    error: Optional[str] = None

# AI Job Analyzer
class JobAnalyzer:
    def __init__(self, ollama_endpoint: str = "http://localhost:11434", model: str = "llama3:latest"):
        self.ollama_endpoint = ollama_endpoint
        self.model = model
        self.ollama_available = self._check_ollama_availability()
        self.available = self.ollama_available
        
    def _check_ollama_availability(self) -> bool:
        try:
            response = requests.get(f"{self.ollama_endpoint}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
            

    
    def query_ollama(self, prompt: str, max_tokens: int = 1024) -> Optional[str]:
        if not self.ollama_available:
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
            

            
    def query_ai(self, prompt: str, max_tokens: int = 1024) -> Optional[str]:
        """Query AI service (Ollama)"""
        if self.ollama_available:
            response = self.query_ollama(prompt, max_tokens)
            if response:
                logger.info("Using Ollama for AI analysis")
                return response
                
        return None
    
    def analyze_job_compatibility(self, job_data: JobData, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        if not self.available:
            return self._fallback_analysis(job_data, user_profile)
        
        prompt = f"""
        Analyze this job posting for compatibility with the user profile:
        
        Job: {job_data.title} at {job_data.company}
        Location: {job_data.location}
        Description: {job_data.description[:500]}...
        
        User Profile:
        - Skills: {', '.join(user_profile.get('skills', []))}
        - Experience: {user_profile.get('experience_years', 0)} years
        - Preferred Location: {', '.join(user_profile.get('preferred_locations', []))}
        - Salary Range: ${user_profile.get('salary_min', 0)} - ${user_profile.get('salary_max', 0)}
        
        Provide a JSON response with:
        {{
            "compatibility_score": 0-100,
            "skill_match_score": 0-100,
            "should_apply": true/false,
            "reasoning": "detailed explanation",
            "skill_gaps": ["gap1", "gap2"],
            "skill_matches": ["match1", "match2"]
        }}
        """
        
        response = self.query_ai(prompt)
        if response:
            try:
                return json.loads(response)
            except:
                pass
        
        return self._fallback_analysis(job_data, user_profile)
    
    def _fallback_analysis(self, job_data: JobData, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        # Simple keyword matching fallback
        user_skills = set(user_profile.get('skills', []))
        job_desc = job_data.description.lower()
        
        matches = [skill for skill in user_skills if skill.lower() in job_desc]
        score = min(100, len(matches) * 20)
        
        return {
            "compatibility_score": score,
            "skill_match_score": score,
            "should_apply": score > 50,
            "reasoning": f"Found {len(matches)} skill matches: {', '.join(matches)}",
            "skill_gaps": [],
            "skill_matches": matches
        }
    
    def generate_cover_letter(self, job_data: JobData, user_profile: Dict[str, Any]) -> str:
        if not self.available:
            return self._fallback_cover_letter(job_data, user_profile)
        
        prompt = f"""
        Generate a professional cover letter for this job:
        
        Job: {job_data.title} at {job_data.company}
        Description: {job_data.description[:300]}...
        
        User Profile:
        - Name: {user_profile.get('name', 'Applicant')}
        - Experience: {user_profile.get('experience_years', 0)} years
        - Skills: {', '.join(user_profile.get('skills', []))}
        - Education: {user_profile.get('education', '')}
        
        Write a compelling cover letter that highlights relevant experience and skills.
        """
        
        response = self.query_ai(prompt)
        if response:
            return response
        
        return self._fallback_cover_letter(job_data, user_profile)
    
    def _fallback_cover_letter(self, job_data: JobData, user_profile: Dict[str, Any]) -> str:
        return f"""
Dear Hiring Manager,

I am excited to apply for the {job_data.title} position at {job_data.company}. With my background in software development and passion for technology, I believe I would be a great fit for your team.

My experience includes {user_profile.get('experience_years', 0)} years in software development, with expertise in {', '.join(user_profile.get('skills', [])[:3])}. I am particularly drawn to this opportunity because it aligns with my career goals and technical interests.

I would welcome the opportunity to discuss how my skills and experience can contribute to {job_data.company}'s success.

Best regards,
{user_profile.get('name', 'Applicant')}
        """.strip()

# Browser Automation Base Class
class BaseAutomation:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.browser = None
        self.wait = None
        
    def setup_browser(self):
        """Setup browser with anti-detection measures"""
        chrome_options = Options()
        
        # Anti-detection options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        chrome_options.add_argument(f"--user-agent={user_agents[0]}")
        
        # Random window size
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.browser = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.browser, 10)
        
        # Apply stealth scripts
        self._apply_stealth_scripts()
        
    def _apply_stealth_scripts(self):
        """Inject JavaScript to hide automation"""
        stealth_script = """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        """
        
        try:
            self.browser.execute_script(stealth_script)
        except Exception as e:
            logger.warning(f"Stealth script failed: {e}")
    
    def _add_random_delay(self, min_delay=1, max_delay=3):
        """Add random delay between actions"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _human_like_typing(self, element, text):
        """Type text character by character like a human"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(0.1)
    
    def _simulate_human_behavior(self):
        """Simulate human-like behavior"""
        # Random mouse movement
        actions = ActionChains(self.browser)
        actions.move_by_offset(10, 10)
        actions.perform()
        
        # Random scroll
        self.browser.execute_script("window.scrollBy(0, 100);")
        time.sleep(0.5)
    
    def close_browser(self):
        """Close browser safely"""
        if self.browser:
            try:
                self.browser.quit()
            except:
                pass
            self.browser = None

# LinkedIn Automation
class LinkedInAutomation(BaseAutomation):
    def __init__(self, config: Dict[str, Any], user_profile: Dict[str, Any]):
        super().__init__(config)
        self.user_profile = user_profile
        self.credentials = config.get('linkedin', {}).get('credentials', {})
        
    def login(self) -> bool:
        """Login to LinkedIn"""
        try:
            self.browser.get("https://www.linkedin.com/login")
            self._add_random_delay()
            
            # Enter email
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            self._human_like_typing(email_field, self.credentials.get('email', ''))
            
            # Enter password
            password_field = self.browser.find_element(By.ID, "password")
            self._human_like_typing(password_field, self.credentials.get('password', ''))
            
            # Click login
            login_button = self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login
            self.wait.until(EC.presence_of_element_located((By.ID, "global-nav")))
            logger.info("LinkedIn login successful")
            return True
            
        except Exception as e:
            logger.error(f"LinkedIn login failed: {e}")
            return False
    
    def search_jobs(self, keywords: str, location: str = "Remote") -> List[JobData]:
        """Search for jobs on LinkedIn"""
        try:
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}"
            self.browser.get(search_url)
            self._add_random_delay()
            
            jobs = []
            job_cards = self.browser.find_elements(By.CSS_SELECTOR, ".job-search-card")
            
            for card in job_cards[:10]:  # Limit to 10 jobs
                try:
                    title = card.find_element(By.CSS_SELECTOR, ".job-search-card__title").text
                    company = card.find_element(By.CSS_SELECTOR, ".job-search-card__subtitle").text
                    location_elem = card.find_element(By.CSS_SELECTOR, ".job-search-card__location")
                    location_text = location_elem.text if location_elem else "Remote"
                    
                    # Get job URL
                    link_elem = card.find_element(By.CSS_SELECTOR, "a")
                    job_url = link_elem.get_attribute("href")
                    
                    jobs.append(JobData(
                        title=title,
                        company=company,
                        location=location_text,
                        description="",  # Will be filled later
                        url=job_url,
                        platform="LinkedIn",
                        posted_date=datetime.now().strftime("%Y-%m-%d")
                    ))
                    
                except Exception as e:
                    logger.warning(f"Error parsing job card: {e}")
                    continue
            
            return jobs
            
        except Exception as e:
            logger.error(f"LinkedIn job search failed: {e}")
            return []
    
    def apply_to_job(self, job: JobData) -> ApplicationResult:
        """Apply to a specific job"""
        try:
            self.browser.get(job.url)
            self._add_random_delay()
            
            # Look for Easy Apply button
            easy_apply_button = self.browser.find_element(By.CSS_SELECTOR, ".jobs-apply-button")
            easy_apply_button.click()
            
            # Fill application form
            self._fill_application_form()
            
            # Submit application
            submit_button = self.browser.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']")
            submit_button.click()
            
            return ApplicationResult(
                job_title=job.title,
                company=job.company,
                platform="LinkedIn",
                status="Applied",
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"LinkedIn application failed: {e}")
            return ApplicationResult(
                job_title=job.title,
                company=job.company,
                platform="LinkedIn",
                status="Failed",
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )
    
    def _fill_application_form(self):
        """Fill out the application form"""
        try:
            # Fill personal information
            name_field = self.browser.find_element(By.NAME, "name")
            self._human_like_typing(name_field, self.user_profile.get('name', ''))
            
            email_field = self.browser.find_element(By.NAME, "email")
            self._human_like_typing(email_field, self.user_profile.get('email', ''))
            
            phone_field = self.browser.find_element(By.NAME, "phone")
            self._human_like_typing(phone_field, self.user_profile.get('phone', ''))
            
            self._add_random_delay()
            
        except Exception as e:
            logger.warning(f"Form filling error: {e}")

# Indeed Automation
class IndeedAutomation(BaseAutomation):
    def __init__(self, config: Dict[str, Any], user_profile: Dict[str, Any]):
        super().__init__(config)
        self.user_profile = user_profile
        
    def search_jobs(self, keywords: str, location: str = "Remote") -> List[JobData]:
        """Search for jobs on Indeed"""
        try:
            search_url = f"https://www.indeed.com/jobs?q={keywords}&l={location}"
            self.browser.get(search_url)
            self._add_random_delay()
            
            jobs = []
            job_cards = self.browser.find_elements(By.CSS_SELECTOR, ".job_seen_beacon")
            
            for card in job_cards[:10]:
                try:
                    title = card.find_element(By.CSS_SELECTOR, "h2.jobTitle").text
                    company = card.find_element(By.CSS_SELECTOR, ".companyName").text
                    location_elem = card.find_element(By.CSS_SELECTOR, ".companyLocation")
                    location_text = location_elem.text if location_elem else "Remote"
                    
                    jobs.append(JobData(
                        title=title,
                        company=company,
                        location=location_text,
                        description="",
                        url="",
                        platform="Indeed",
                        posted_date=datetime.now().strftime("%Y-%m-%d")
                    ))
                    
                except Exception as e:
                    logger.warning(f"Error parsing Indeed job card: {e}")
                    continue
            
            return jobs
            
        except Exception as e:
            logger.error(f"Indeed job search failed: {e}")
            return []

# Glassdoor Automation
class GlassdoorAutomation(BaseAutomation):
    def __init__(self, config: Dict[str, Any], user_profile: Dict[str, Any]):
        super().__init__(config)
        self.user_profile = user_profile
        
    def search_jobs(self, keywords: str, location: str = "Remote") -> List[JobData]:
        """Search for jobs on Glassdoor"""
        try:
            search_url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keywords}&locT=N&locId=1"
            self.browser.get(search_url)
            self._add_random_delay()
            
            jobs = []
            job_cards = self.browser.find_elements(By.CSS_SELECTOR, ".react-job-listing")
            
            for card in job_cards[:10]:
                try:
                    title = card.find_element(By.CSS_SELECTOR, ".jobLink").text
                    company = card.find_element(By.CSS_SELECTOR, ".employerName").text
                    location_elem = card.find_element(By.CSS_SELECTOR, ".location")
                    location_text = location_elem.text if location_elem else "Remote"
                    
                    jobs.append(JobData(
                        title=title,
                        company=company,
                        location=location_text,
                        description="",
                        url="",
                        platform="Glassdoor",
                        posted_date=datetime.now().strftime("%Y-%m-%d")
                    ))
                    
                except Exception as e:
                    logger.warning(f"Error parsing Glassdoor job card: {e}")
                    continue
            
            return jobs
            
        except Exception as e:
            logger.error(f"Glassdoor job search failed: {e}")
            return []

# Multi-Platform Manager
class MultiPlatformManager:
    def __init__(self, config: Dict[str, Any], user_profile: Dict[str, Any]):
        self.config = config
        self.user_profile = user_profile
        self.analyzer = JobAnalyzer()
        self.automations = {}
        
    def setup_automations(self):
        """Setup automation for each platform"""
        job_sites = self.config.get('job_sites', {})
        
        if job_sites.get('linkedin', {}).get('enabled', False):
            self.automations['linkedin'] = LinkedInAutomation(self.config, self.user_profile)
        
        if job_sites.get('indeed', {}).get('enabled', False):
            self.automations['indeed'] = IndeedAutomation(self.config, self.user_profile)
        
        if job_sites.get('glassdoor', {}).get('enabled', False):
            self.automations['glassdoor'] = GlassdoorAutomation(self.config, self.user_profile)
    
    def run_automation(self, platform: str = None) -> Dict[str, Any]:
        """Run automation for specified platform or all platforms"""
        results = {
            'jobs_found': 0,
            'applications_sent': 0,
            'errors': [],
            'platforms': {}
        }
        
        try:
            # Only run specific platform if specified, otherwise run all
            if platform and platform.lower() in [p.lower() for p in self.automations.keys()]:
                # Find the correct case for the platform name
                platform_key = next((k for k in self.automations.keys() if k.lower() == platform.lower()), None)
                if platform_key:
                    results['platforms'][platform_key] = self._run_single_platform(platform_key)
            elif platform and platform.lower() == 'all':
                # Run all platforms only when explicitly requested
                for platform_name in self.automations:
                    results['platforms'][platform_name] = self._run_single_platform(platform_name)
            else:
                # Default behavior: run only the first available platform
                if self.automations:
                    first_platform = list(self.automations.keys())[0]
                    results['platforms'][first_platform] = self._run_single_platform(first_platform)
            
            # Calculate totals
            for platform_result in results['platforms'].values():
                results['jobs_found'] += platform_result.get('jobs_found', 0)
                results['applications_sent'] += platform_result.get('applications_sent', 0)
                results['errors'].extend(platform_result.get('errors', []))
            
        except Exception as e:
            results['errors'].append(str(e))
            logger.error(f"Automation failed: {e}")
        
        return results
    
    def _run_single_platform(self, platform: str) -> Dict[str, Any]:
        """Run automation for a single platform"""
        automation = self.automations[platform]
        results = {
            'jobs_found': 0,
            'applications_sent': 0,
            'errors': [],
            'jobs': []
        }
        
        try:
            # Setup browser
            automation.setup_browser()
            
            # Login if needed
            if platform == 'linkedin':
                if not automation.login():
                    results['errors'].append("LinkedIn login failed")
                    return results
            
            # Search for jobs
            keywords = self.config.get('job_criteria', {}).get('required_keywords', ['Software Engineer'])
            location = self.config.get('job_criteria', {}).get('locations', ['Remote'])[0]
            
            jobs = automation.search_jobs(keywords[0], location)
            results['jobs_found'] = len(jobs)
            results['jobs'] = [asdict(job) for job in jobs]
            
            # Analyze and apply to jobs
            for job in jobs:
                try:
                    # Analyze job compatibility
                    analysis = self.analyzer.analyze_job_compatibility(job, self.user_profile)
                    
                    if analysis.get('should_apply', False):
                        # Apply to job
                        application_result = automation.apply_to_job(job)
                        if application_result.status == "Applied":
                            results['applications_sent'] += 1
                        else:
                            results['errors'].append(f"Failed to apply to {job.title}: {application_result.error}")
                    
                    self._add_random_delay(30, 60)  # Delay between applications
                    
                except Exception as e:
                    results['errors'].append(f"Error processing job {job.title}: {e}")
            
        except Exception as e:
            results['errors'].append(f"Platform {platform} failed: {e}")
        
        # Don't close browser automatically - let user control it
        # automation.close_browser()
        
        return results
    
    def _add_random_delay(self, min_delay=30, max_delay=60):
        """Add random delay between applications"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

# Flask Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get current automation status"""
    return jsonify({
        'is_running': app_state.is_running,
        'current_platform': app_state.current_platform,
        'jobs_found': app_state.jobs_found,
        'applications_sent': app_state.applications_sent,
        'errors': app_state.errors[-10:],  # Last 10 errors
        'logs': app_state.logs[-20:]  # Last 20 logs
    })

@app.route('/api/start', methods=['POST'])
def start_automation():
    """Start automation"""
    if app_state.is_running:
        return jsonify({'error': 'Automation already running'}), 400
    
    try:
        data = request.get_json()
        platform = data.get('platform')  # None for all platforms
        
        # Load configuration
        with open('config.json', 'r') as f:
            app_state.config = json.load(f)
        
        with open('my_details.json', 'r') as f:
            app_state.user_profile = json.load(f)
        
        # Initialize analyzer
        app_state.analyzer = JobAnalyzer()
        
        # Start automation in background thread
        def run_automation():
            app_state.is_running = True
            app_state.current_platform = platform or "All Platforms"
            
            try:
                manager = MultiPlatformManager(app_state.config, app_state.user_profile)
                app_state.manager = manager  # Store manager instance
                manager.setup_automations()
                
                results = manager.run_automation(platform)
                
                app_state.jobs_found = results['jobs_found']
                app_state.applications_sent = results['applications_sent']
                app_state.errors.extend(results['errors'])
                
                # Save results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(f'automation_results_{timestamp}.json', 'w') as f:
                    json.dump(results, f, indent=2)
                
            except Exception as e:
                app_state.errors.append(str(e))
                logger.error(f"Automation failed: {e}")
            finally:
                app_state.is_running = False
                app_state.current_platform = None
        
        thread = threading.Thread(target=run_automation)
        thread.daemon = True
        thread.start()
        
        return jsonify({'message': 'Automation started successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_automation():
    """Stop automation"""
    app_state.is_running = False
    app_state.current_platform = None
    
    # Close all automation browsers
    if hasattr(app_state, 'manager') and app_state.manager:
        for automation in app_state.manager.automations.values():
            if hasattr(automation, 'browser') and automation.browser:
                try:
                    automation.close_browser()
                except:
                    pass
    
    return jsonify({'message': 'Automation stopped'})

@app.route('/api/close-browser', methods=['POST'])
def close_browser():
    """Manually close browser"""
    try:
        if hasattr(app_state, 'manager') and app_state.manager:
            for automation in app_state.manager.automations.values():
                if hasattr(automation, 'browser') and automation.browser:
                    automation.close_browser()
        return jsonify({'message': 'Browser closed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_job():
    """Analyze a job posting"""
    try:
        data = request.get_json()
        job_data = JobData(**data['job'])
        
        if not app_state.analyzer:
            app_state.analyzer = JobAnalyzer()
        
        analysis = app_state.analyzer.analyze_job_compatibility(job_data, app_state.user_profile)
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cover-letter', methods=['POST'])
def generate_cover_letter():
    """Generate cover letter for a job"""
    try:
        data = request.get_json()
        job_data = JobData(**data['job'])
        
        if not app_state.analyzer:
            app_state.analyzer = JobAnalyzer()
        
        cover_letter = app_state.analyzer.generate_cover_letter(job_data, app_state.user_profile)
        
        return jsonify({'cover_letter': cover_letter})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """Get or update configuration"""
    if request.method == 'GET':
        try:
            with open('config.json', 'r') as f:
                return jsonify(json.load(f))
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            config = request.get_json()
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=2)
            return jsonify({'message': 'Configuration updated'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Create templates directory and dashboard template
def create_dashboard_template():
    """Create the dashboard HTML template"""
    os.makedirs('templates', exist_ok=True)
    
    dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Automation Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .card { border: none; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        .btn-primary { background: linear-gradient(45deg, #667eea, #764ba2); border: none; }
        .status-running { color: #28a745; }
        .status-stopped { color: #dc3545; }
        .log-entry { font-family: 'Courier New', monospace; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <div class="row">
            <div class="col-12">
                <div class="card mb-4">
                    <div class="card-header bg-primary text-white">
                        <h2 class="mb-0"><i class="fas fa-robot"></i> Job Automation Dashboard</h2>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="d-grid gap-2">
                                    <button id="startBtn" class="btn btn-success btn-lg">
                                        <i class="fas fa-play"></i> Start Automation
                                    </button>
                                    <button id="stopBtn" class="btn btn-danger btn-lg" disabled>
                                        <i class="fas fa-stop"></i> Stop Automation
                                    </button>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-body text-center">
                                        <h5>Status</h5>
                                        <div id="status" class="status-stopped">
                                            <i class="fas fa-circle"></i> Stopped
                                        </div>
                                        <div id="platform" class="text-muted">No platform selected</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-bar"></i> Statistics</h5>
                    </div>
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-6">
                                <h3 id="jobsFound">0</h3>
                                <p class="text-muted">Jobs Found</p>
                            </div>
                            <div class="col-6">
                                <h3 id="applicationsSent">0</h3>
                                <p class="text-muted">Applications Sent</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-cog"></i> Configuration</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <label class="form-label">Platform</label>
                                <select id="platformSelect" class="form-select">
                                    <option value="">All Platforms</option>
                                    <option value="linkedin">LinkedIn</option>
                                    <option value="indeed">Indeed</option>
                                    <option value="glassdoor">Glassdoor</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Strategy</label>
                                <select id="strategySelect" class="form-select">
                                    <option value="conservative">Conservative</option>
                                    <option value="moderate">Moderate</option>
                                    <option value="aggressive">Aggressive</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-list"></i> Recent Logs</h5>
                    </div>
                    <div class="card-body">
                        <div id="logs" class="log-container" style="max-height: 300px; overflow-y: auto;">
                            <div class="text-muted">No logs yet...</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-exclamation-triangle"></i> Errors</h5>
                    </div>
                    <div class="card-body">
                        <div id="errors" class="log-container" style="max-height: 300px; overflow-y: auto;">
                            <div class="text-muted">No errors yet...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let isRunning = false;
        
        // Update status
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    isRunning = data.is_running;
                    
                    // Update buttons
                    document.getElementById('startBtn').disabled = isRunning;
                    document.getElementById('stopBtn').disabled = !isRunning;
                    
                    // Update status
                    const statusEl = document.getElementById('status');
                    if (isRunning) {
                        statusEl.className = 'status-running';
                        statusEl.innerHTML = '<i class="fas fa-circle"></i> Running';
                    } else {
                        statusEl.className = 'status-stopped';
                        statusEl.innerHTML = '<i class="fas fa-circle"></i> Stopped';
                    }
                    
                    // Update platform
                    document.getElementById('platform').textContent = data.current_platform || 'No platform selected';
                    
                    // Update statistics
                    document.getElementById('jobsFound').textContent = data.jobs_found;
                    document.getElementById('applicationsSent').textContent = data.applications_sent;
                    
                    // Update logs
                    updateLogs(data.logs);
                    updateErrors(data.errors);
                })
                .catch(error => console.error('Error updating status:', error));
        }
        
        function updateLogs(logs) {
            const logsEl = document.getElementById('logs');
            if (logs.length > 0) {
                logsEl.innerHTML = logs.map(log => 
                    `<div class="log-entry">${log}</div>`
                ).join('');
            }
        }
        
        function updateErrors(errors) {
            const errorsEl = document.getElementById('errors');
            if (errors.length > 0) {
                errorsEl.innerHTML = errors.map(error => 
                    `<div class="log-entry text-danger">${error}</div>`
                ).join('');
            }
        }
        
        // Event listeners
        document.getElementById('startBtn').addEventListener('click', () => {
            const platform = document.getElementById('platformSelect').value;
            const strategy = document.getElementById('strategySelect').value;
            
            fetch('/api/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ platform, strategy })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    alert('Automation started successfully!');
                }
            })
            .catch(error => {
                console.error('Error starting automation:', error);
                alert('Error starting automation');
            });
        });
        
        document.getElementById('stopBtn').addEventListener('click', () => {
            fetch('/api/stop', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                alert('Automation stopped');
            })
            .catch(error => {
                console.error('Error stopping automation:', error);
                alert('Error stopping automation');
            });
        });
        
        // Update status every 2 seconds
        setInterval(updateStatus, 2000);
        updateStatus();
    </script>
</body>
</html>
    """
    
    with open('templates/dashboard.html', 'w') as f:
        f.write(dashboard_html)

if __name__ == '__main__':
    # Create dashboard template
    create_dashboard_template()
    
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            app_state.config = json.load(f)
    except FileNotFoundError:
        logger.error("config.json not found. Please create it first.")
        exit(1)
    
    try:
        with open('my_details.json', 'r') as f:
            app_state.user_profile = json.load(f)
    except FileNotFoundError:
        logger.error("my_details.json not found. Please run setup_my_details.py first.")
        exit(1)
    
    # Initialize analyzer
    app_state.analyzer = JobAnalyzer()
    
    print("🚀 Starting Unified Job Automation Application...")
    print("📊 Dashboard available at: http://localhost:5000")
    print("🔧 Make sure Ollama is running for AI features")
    print("🌐 Press Ctrl+C to stop the application")
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000) 