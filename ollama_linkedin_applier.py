#!/usr/bin/env python3
"""
🚀 Ollama-Enhanced LinkedIn Job Applier
Uses local Ollama for intelligent job application handling
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import json
import os
import subprocess
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
from PIL import Image
import requests

class OllamaLinkedInApplier:
    def __init__(self, profile_path="user_profile.json"):
        """Initialize with user profile and Ollama"""
        load_dotenv()
        
        # Load user profile
        try:
            with open(profile_path, 'r') as f:
                self.profile = json.load(f)
            print("✅ User profile loaded successfully")
        except FileNotFoundError:
            print(f"❌ Profile file {profile_path} not found!")
            raise
        
        # LinkedIn credentials
        self.email = self.profile['personal_info']['email']
        self.password = os.getenv('LINKEDIN_PASSWORD', 'Mani!8897')
        
        # Job search criteria
        search_criteria = self.profile['search_criteria']
        self.keywords = search_criteria['keywords'][0]
        self.location = search_criteria['locations'][0]
        self.max_applications = 25
        self.applications_sent = 0
        
        print(f"🔐 Using email: {self.email}")
        print(f"🔍 Search criteria: {self.keywords} in {self.location}")
        print(f"🎯 Max applications: {self.max_applications}")
        
        # Setup Ollama
        self.setup_ollama()
        
        # Setup Chrome
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 15)
        
        # Load Easy Apply templates
        self.easy_apply_templates = self.load_easy_apply_templates()

    def setup_ollama(self):
        """Setup and verify Ollama connection"""
        print("🧠 Setting up Ollama...")
        
        try:
            # Check if Ollama is running
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                models = result.stdout.strip()
                print("✅ Ollama is running")
                
                # Find available model
                if 'qwen2.5:7b' in models:
                    self.ollama_model = "qwen2.5:7b"
                elif 'llama3.1:8b' in models:
                    self.ollama_model = "llama3.1:8b"
                elif 'llama3.1:70b' in models:
                    self.ollama_model = "llama3.1:70b"
                elif models and 'NAME' in models:
                    lines = models.split('\n')[1:]
                    if lines:
                        self.ollama_model = lines[0].split()[0]
                else:
                    print("❌ No Ollama models found!")
                    print("💡 Install a model with: ollama pull qwen2.5:7b")
                    raise Exception("No Ollama models available")
                
                print(f"🧠 Using Ollama model: {self.ollama_model}")
                self.ollama_available = True
                
            else:
                print("❌ Ollama not responding")
                self.ollama_available = False
                
        except FileNotFoundError:
            print("❌ Ollama not installed")
            self.ollama_available = False
        except Exception as e:
            print(f"❌ Ollama setup error: {e}")
            self.ollama_available = False

    def query_ollama(self, prompt, max_tokens=500):
        """Query Ollama for intelligent responses"""
        if not self.ollama_available:
            return None
        
        try:
            # Use Ollama API
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': self.ollama_model,
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
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"⚠️ Ollama API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️ Ollama query error: {e}")
            return None

    def analyze_job_with_ollama(self, job_title, company, job_description=""):
        """Use Ollama to analyze if job is worth applying to"""
        if not self.ollama_available:
            return True  # Default to applying if Ollama not available
        
        prompt = f"""
Analyze this job opportunity for a Python developer:

Job Title: {job_title}
Company: {company}
Description: {job_description[:500]}...

My Profile:
- Skills: {', '.join(self.profile['skills']['programming_languages'])}
- Experience: {self.profile['work_experience'][0]['position'] if self.profile['work_experience'] else 'Python Developer'}
- Preferences: {', '.join(self.profile['job_preferences']['desired_positions'])}

Should I apply to this job? Consider:
1. Skill match
2. Career progression
3. Company reputation
4. Job requirements

Respond with only: YES or NO, followed by a brief reason.
"""
        
        response = self.query_ollama(prompt, max_tokens=100)
        
        if response:
            if response.upper().startswith('YES'):
                print(f"🧠 Ollama recommends: APPLY - {response}")
                return True
            else:
                print(f"🧠 Ollama recommends: SKIP - {response}")
                return False
        
        return True  # Default to applying if analysis fails

    def generate_cover_letter_with_ollama(self, job_title, company):
        """Generate personalized cover letter using Ollama"""
        if not self.ollama_available:
            return self.profile['cover_letter_templates']['default'].format(
                position=job_title,
                company=company,
                experience_years="5+",
                full_name=self.profile['personal_info']['full_name'],
                custom_paragraph="I am excited about this opportunity to contribute to your team."
            )
        
        prompt = f"""
Write a professional cover letter for this job application:

Job Title: {job_title}
Company: {company}

My Background:
- Name: {self.profile['personal_info']['full_name']}
- Current Role: {self.profile['work_experience'][0]['position'] if self.profile['work_experience'] else 'Python Developer'}
- Skills: {', '.join(self.profile['skills']['programming_languages'][:3])}
- Experience: 5+ years in Python development

Requirements:
- Keep it concise (3-4 sentences)
- Professional tone
- Highlight relevant skills
- Show enthusiasm
- No generic phrases

Format: Just the cover letter text, no subject line.
"""
        
        response = self.query_ollama(prompt, max_tokens=200)
        
        if response:
            print("🧠 Generated personalized cover letter with Ollama")
            return response
        else:
            # Fallback to template
            return self.profile['cover_letter_templates']['default'].format(
                position=job_title,
                company=company,
                experience_years="5+",
                full_name=self.profile['personal_info']['full_name'],
                custom_paragraph="I am excited about this opportunity to contribute to your team."
            )

    def smart_form_filling_with_ollama(self, field_label, field_type="text"):
        """Use Ollama to intelligently fill form fields"""
        if not self.ollama_available:
            return self.get_profile_value_for_field(field_label)
        
        prompt = f"""
I need to fill a job application form field. Based on my profile, what should I enter?

Field Label: "{field_label}"
Field Type: {field_type}

My Profile:
- Name: {self.profile['personal_info']['full_name']}
- Email: {self.profile['personal_info']['email']}
- Phone: {self.profile['personal_info']['phone']}
- Experience: 5+ years Python development
- Current Company: {self.profile['work_experience'][0]['company'] if self.profile['work_experience'] else 'Tech Company'}
- Skills: {', '.join(self.profile['skills']['programming_languages'][:5])}
- Salary Range: {self.profile['application_responses']['salary_expectations']['range']}

Respond with ONLY the value to enter, no explanation. Keep it concise and professional.
"""
        
        response = self.query_ollama(prompt, max_tokens=50)
        
        if response and len(response.strip()) > 0:
            return response.strip()
        else:
            return self.get_profile_value_for_field(field_label)

    def get_profile_value_for_field(self, field_label):
        """Get appropriate profile value for a field (fallback method)"""
        field_label_lower = field_label.lower()
        
        if any(word in field_label_lower for word in ['first', 'given', 'fname']):
            return self.profile['personal_info']['first_name']
        elif any(word in field_label_lower for word in ['last', 'family', 'lname', 'surname']):
            return self.profile['personal_info']['last_name']
        elif 'email' in field_label_lower:
            return self.profile['personal_info']['email']
        elif 'phone' in field_label_lower:
            return self.profile['personal_info']['phone']
        elif any(word in field_label_lower for word in ['salary', 'compensation', 'pay']):
            return self.profile['application_responses']['salary_expectations']['range']
        elif any(word in field_label_lower for word in ['experience', 'years']):
            return "5+"
        elif any(word in field_label_lower for word in ['availability', 'start']):
            return self.profile['application_responses']['availability']['start_date']
        else:
            return ""

    def load_easy_apply_templates(self):
        """Load Easy Apply button templates for computer vision"""
        templates = []
        template_files = [
            "easy apply image1.png",
            "easy apply image2.webp"
        ]
        
        for template_file in template_files:
            try:
                if os.path.exists(template_file):
                    img = cv2.imread(template_file, cv2.IMREAD_COLOR)
                    if img is not None:
                        gray_template = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        templates.append({
                            'image': gray_template,
                            'name': template_file,
                            'height': gray_template.shape[0],
                            'width': gray_template.shape[1]
                        })
                        print(f"✅ Loaded Easy Apply template: {template_file}")
            except Exception as e:
                print(f"⚠️ Error loading template {template_file}: {e}")
        
        if templates:
            print(f"✅ Loaded {len(templates)} Easy Apply templates")
        else:
            print("⚠️ No Easy Apply templates loaded - using traditional selectors only")
        
        return templates

    def human_delay(self, min_sec=1, max_sec=3):
        """Human-like random delays"""
        time.sleep(random.uniform(min_sec, max_sec))

    def type_like_human(self, element, text):
        """Type with human-like delays"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    def show_manual_intervention_popup(self, title, message, instructions=""):
        """Show reliable manual intervention popup"""
        print(f"\n🚨 MANUAL INTERVENTION REQUIRED: {title}")
        print("=" * 60)
        print(f"📋 {message}")
        if instructions:
            print(f"💡 {instructions}")
        print("=" * 60)

        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            root.lift()
            root.focus_force()

            full_message = f"{message}\n\n{instructions}" if instructions else message

            messagebox.showinfo(
                "🚨 LINKEDIN AUTOMATION - MANUAL ACTION REQUIRED 🚨",
                full_message
            )

            root.destroy()
            print("✅ User completed manual intervention!")
            return True

        except Exception as e:
            print(f"⚠️ Popup failed: {e}")
            print("⌨️ Press ENTER after completing the action...")
            try:
                input()
                return True
            except:
                return False

    def detect_manual_intervention_needed(self):
        """Detect if manual intervention is needed"""
        current_url = self.driver.current_url.lower()
        page_source = self.driver.page_source.lower()

        interventions = {
            'captcha': {
                'indicators': ['captcha', 'recaptcha', 'verify you are human', 'security check'],
                'title': '🤖 CAPTCHA Detected',
                'message': 'LinkedIn is asking you to complete a CAPTCHA puzzle.\n\nPlease solve the CAPTCHA in the browser window.',
                'instructions': 'Click "OK" after completing the CAPTCHA to continue automation'
            },
            'security_challenge': {
                'indicators': ['challenge', 'security', 'verify', 'suspicious activity'],
                'title': '🔒 Security Challenge',
                'message': 'LinkedIn has detected unusual activity.\n\nPlease complete the security challenge.',
                'instructions': 'Follow LinkedIn\'s instructions, then click "OK" to continue'
            }
        }

        for intervention_type, config in interventions.items():
            for indicator in config['indicators']:
                if indicator in current_url or indicator in page_source:
                    return self.show_manual_intervention_popup(
                        config['title'], config['message'], config['instructions']
                    )

        return False

    def login_linkedin(self):
        """Login to LinkedIn"""
        print(f"🔐 Logging into LinkedIn...")

        try:
            self.driver.get("https://www.linkedin.com/login")
            self.human_delay(2, 4)

            # Enter email
            email_field = self.wait.until(EC.presence_of_element_located((By.NAME, 'session_key')))
            self.type_like_human(email_field, self.email)
            print(f"✅ Email entered")
            self.human_delay(1, 2)

            # Enter password
            password_field = self.driver.find_element(By.NAME, 'session_password')
            self.type_like_human(password_field, self.password)
            print("✅ Password entered")
            self.human_delay(1, 2)

            # Submit login
            password_field.send_keys(Keys.RETURN)
            self.human_delay(5, 8)

            # Check for manual intervention and login success
            for attempt in range(3):
                current_url = self.driver.current_url.lower()
                print(f"📍 Login attempt {attempt + 1}: {current_url}")

                if any(indicator in current_url for indicator in ["feed", "/in/", "jobs"]):
                    print("✅ Login successful!")
                    return True

                if self.detect_manual_intervention_needed():
                    self.human_delay(2, 3)
                    continue

                if "login" in current_url:
                    print("❌ Login failed")
                    return False

                self.human_delay(3, 5)

            return False

        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False

    def navigate_to_jobs_and_search(self):
        """Navigate to jobs page and perform search"""
        print("🧭 Navigating to Jobs section and performing search...")

        try:
            # Go directly to jobs search with parameters
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={self.keywords.replace(' ', '%20')}&location={self.location.replace(' ', '%20')}&f_LF=f_AL"
            print(f"🔍 Searching with URL: {search_url}")

            self.driver.get(search_url)
            self.human_delay(5, 8)

            # Verify we're on the jobs page
            current_url = self.driver.current_url.lower()
            if "jobs" not in current_url:
                print("❌ Failed to navigate to jobs page")
                return False

            print("✅ Successfully navigated to jobs search page")

            # Verify search results
            return self.verify_search_results()

        except Exception as e:
            print(f"❌ Navigation/search failed: {e}")
            return False

    def verify_search_results(self):
        """Verify that search results are displayed"""
        print("🔍 Verifying search results...")

        try:
            self.human_delay(3, 5)

            # Check for job results
            result_selectors = [
                ".jobs-search-results__list-item",
                ".job-card-container",
                "[data-job-id]",
                ".jobs-search-results-list__item"
            ]

            for selector in result_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ Found {len(elements)} job results!")
                        return True
                except:
                    continue

            print("❌ No job results found")
            return False

        except Exception as e:
            print(f"❌ Error verifying results: {e}")
            return False

    def get_job_listings(self):
        """Get job listings from current page"""
        try:
            selectors = [
                ".jobs-search-results__list-item",
                ".job-card-container",
                "[data-job-id]",
                ".scaffold-layout__list-item",
                ".jobs-search-results-list__item"
            ]

            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ Found {len(elements)} job listings using: {selector}")
                        return elements
                except:
                    continue

            print("❌ No job listings found")
            return []

        except Exception as e:
            print(f"❌ Error getting job listings: {e}")
            return []

    def find_easy_apply_button_enhanced(self):
        """Enhanced Easy Apply button detection with computer vision"""
        print("🔍 Searching for Easy Apply button with enhanced detection...")

        # Method 1: Computer Vision (if templates available)
        if self.easy_apply_templates:
            print("🤖 Trying computer vision detection...")
            try:
                screenshot = self.driver.get_screenshot_as_png()
                img_array = np.frombuffer(screenshot, np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                for template in self.easy_apply_templates:
                    result = cv2.matchTemplate(gray_img, template['image'], cv2.TM_CCOEFF_NORMED)
                    threshold = 0.7
                    locations = np.where(result >= threshold)

                    for pt in zip(*locations[::-1]):
                        x, y = pt
                        w, h = template['width'], template['height']
                        center_x = x + w // 2
                        center_y = y + h // 2

                        print(f"✅ Found Easy Apply button using CV at ({center_x}, {center_y})")
                        return {'type': 'cv', 'x': center_x, 'y': center_y}

            except Exception as e:
                print(f"⚠️ CV detection failed: {e}")

        # Method 2: Enhanced traditional selectors
        print("🔍 Trying enhanced selector detection...")
        selectors = [
            "//button[contains(@aria-label, 'Easy Apply')]",
            "//button[contains(text(), 'Easy Apply')]",
            "//span[contains(text(), 'Easy Apply')]/parent::button",
            ".jobs-apply-button",
            "[data-control-name*='apply']",
            "//button[contains(@class, 'jobs-apply-button')]",
            ".jobs-s-apply button",
            "//a[contains(@href, 'easy-apply')]"
        ]

        for selector in selectors:
            try:
                if selector.startswith("//"):
                    button = self.driver.find_element(By.XPATH, selector)
                else:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)

                if button and button.is_displayed() and button.is_enabled():
                    print(f"✅ Found Easy Apply button with selector: {selector}")
                    return {'type': 'selenium', 'element': button}
            except:
                continue

        print("❌ No Easy Apply button found")
        return None

    def click_easy_apply_button_enhanced(self, button_info):
        """Enhanced Easy Apply button clicking"""
        if not button_info:
            return False

        try:
            if button_info['type'] == 'cv':
                # Use computer vision coordinates
                from selenium.webdriver.common.action_chains import ActionChains
                body = self.driver.find_element(By.TAG_NAME, 'body')
                actions = ActionChains(self.driver)
                actions.move_to_element_with_offset(body, button_info['x'], button_info['y'])
                actions.click()
                actions.perform()
                print("✅ Clicked Easy Apply button using computer vision")
                return True
            elif button_info['type'] == 'selenium':
                # Use traditional Selenium click
                button_info['element'].click()
                print("✅ Clicked Easy Apply button using Selenium")
                return True
            else:
                return False

        except Exception as e:
            print(f"❌ Error clicking Easy Apply button: {e}")
            return False

    def apply_to_job_enhanced(self, job_element):
        """Enhanced job application with Ollama intelligence"""
        try:
            # Scroll job into view and click
            self.driver.execute_script("arguments[0].scrollIntoView(true);", job_element)
            self.human_delay(1, 2)

            # Click on the job listing
            job_element.click()
            self.human_delay(3, 5)

            # Check for manual intervention
            if self.detect_manual_intervention_needed():
                return False

            # Extract job information
            job_info = self.extract_job_info()
            print(f"📝 Analyzing job: {job_info['title']} at {job_info['company']}")

            # Use Ollama to analyze if we should apply
            if not self.analyze_job_with_ollama(job_info['title'], job_info['company']):
                print("🧠 Ollama recommends skipping this job")
                return False

            # Find Easy Apply button
            easy_apply_button = self.find_easy_apply_button_enhanced()

            if not easy_apply_button:
                print("❌ No Easy Apply button found, skipping...")
                return False

            # Click Easy Apply
            if not self.click_easy_apply_button_enhanced(easy_apply_button):
                print("❌ Failed to click Easy Apply button, skipping...")
                return False

            self.human_delay(3, 5)

            # Check for manual intervention after clicking
            if self.detect_manual_intervention_needed():
                return False

            # Handle application process with Ollama enhancement
            return self.complete_application_enhanced(job_info)

        except Exception as e:
            print(f"❌ Error applying to job: {e}")
            return False

    def extract_job_info(self):
        """Extract job information from the current job page"""
        job_info = {
            'title': 'Unknown Position',
            'company': 'Unknown Company',
            'location': 'Unknown Location',
            'description': ''
        }

        try:
            # Get job title
            title_selectors = [
                "h1",
                ".job-details-jobs-unified-top-card__job-title",
                ".jobs-unified-top-card__job-title"
            ]

            for selector in title_selectors:
                try:
                    title_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if title_element and title_element.text.strip():
                        job_info['title'] = title_element.text.strip()
                        break
                except:
                    continue

            # Get company name
            company_selectors = [
                ".job-details-jobs-unified-top-card__company-name",
                ".jobs-unified-top-card__company-name",
                "[data-control-name*='company']"
            ]

            for selector in company_selectors:
                try:
                    company_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if company_element and company_element.text.strip():
                        job_info['company'] = company_element.text.strip()
                        break
                except:
                    continue

            # Get job description (first 500 chars for Ollama analysis)
            try:
                desc_element = self.driver.find_element(By.CSS_SELECTOR, ".jobs-description-content__text")
                if desc_element:
                    job_info['description'] = desc_element.text.strip()[:500]
            except:
                pass

        except Exception as e:
            print(f"⚠️ Error extracting job info: {e}")

        return job_info

    def complete_application_enhanced(self, job_info):
        """Complete application with Ollama-enhanced form filling"""
        try:
            max_steps = 5
            current_step = 0

            while current_step < max_steps:
                current_step += 1
                print(f"📋 Application step {current_step}...")

                # Check for manual intervention
                if self.detect_manual_intervention_needed():
                    return True

                # Enhanced form filling with Ollama
                self.fill_application_form_enhanced()

                # Look for submit button
                submit_button = self.find_submit_button()

                if submit_button:
                    submit_button.click()
                    print("✅ Application submitted!")
                    self.applications_sent += 1
                    self.human_delay(3, 5)
                    return True

                # Look for Next/Continue button
                next_button = self.find_next_button()

                if next_button:
                    next_button.click()
                    self.human_delay(2, 3)
                    continue

                # Complex application requiring manual completion
                print("⚠️ Complex application detected")
                if self.show_manual_intervention_popup(
                    "📝 Complex Application",
                    f"The application for {job_info['title']} at {job_info['company']} requires additional information.\n\nPlease complete the application manually in the browser.",
                    "Fill out all required fields and submit, then click 'OK' to continue automation"
                ):
                    self.applications_sent += 1
                    return True
                else:
                    return False

            print("⚠️ Application process exceeded maximum steps")
            return False

        except Exception as e:
            print(f"❌ Error completing application: {e}")
            return False

    def fill_application_form_enhanced(self):
        """Enhanced form filling with Ollama intelligence"""
        try:
            # Find all input fields
            input_fields = self.driver.find_elements(By.CSS_SELECTOR, "input, textarea, select")

            for field in input_fields:
                try:
                    if not field.is_displayed() or not field.is_enabled():
                        continue

                    # Get field information
                    field_label = self.get_field_label(field)
                    field_type = field.get_attribute('type') or 'text'

                    if field_label and field_type in ['text', 'email', 'tel', 'textarea']:
                        # Use Ollama for intelligent field filling
                        value = self.smart_form_filling_with_ollama(field_label, field_type)

                        if value:
                            field.clear()
                            field.send_keys(value)
                            print(f"✅ Filled field '{field_label}': {value}")
                            self.human_delay(0.5, 1)

                except Exception as e:
                    print(f"⚠️ Error filling field: {e}")
                    continue

            # Handle dropdowns
            self.fill_dropdown_fields_enhanced()

        except Exception as e:
            print(f"⚠️ Error in enhanced form filling: {e}")

    def get_field_label(self, field):
        """Get label for a form field"""
        try:
            # Try different methods to get field label
            methods = [
                lambda: field.get_attribute('aria-label'),
                lambda: field.get_attribute('placeholder'),
                lambda: field.get_attribute('name'),
                lambda: field.get_attribute('id'),
                lambda: self.find_label_by_for_attribute(field),
                lambda: self.find_nearby_label(field)
            ]

            for method in methods:
                try:
                    label = method()
                    if label and label.strip():
                        return label.strip()
                except:
                    continue

            return None

        except:
            return None

    def find_label_by_for_attribute(self, field):
        """Find label using 'for' attribute"""
        field_id = field.get_attribute('id')
        if field_id:
            try:
                label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{field_id}']")
                return label.text
            except:
                pass
        return None

    def find_nearby_label(self, field):
        """Find label near the field"""
        try:
            parent = field.find_element(By.XPATH, "..")
            label = parent.find_element(By.CSS_SELECTOR, "label")
            return label.text
        except:
            return None

    def fill_dropdown_fields_enhanced(self):
        """Enhanced dropdown filling"""
        try:
            dropdowns = self.driver.find_elements(By.CSS_SELECTOR, "select")

            for dropdown in dropdowns:
                try:
                    if not dropdown.is_displayed() or not dropdown.is_enabled():
                        continue

                    field_label = self.get_field_label(dropdown)
                    if field_label:
                        # Use Ollama to determine best option
                        value = self.smart_form_filling_with_ollama(field_label, "select")

                        if value:
                            select = Select(dropdown)

                            # Try to select by visible text
                            for option in select.options:
                                if value.lower() in option.text.lower():
                                    select.select_by_visible_text(option.text)
                                    print(f"✅ Selected dropdown '{field_label}': {option.text}")
                                    break

                except Exception as e:
                    print(f"⚠️ Error filling dropdown: {e}")
                    continue

        except Exception as e:
            print(f"⚠️ Error in dropdown filling: {e}")

    def find_submit_button(self):
        """Find submit button"""
        submit_selectors = [
            "//button[contains(@aria-label, 'Submit application')]",
            "//button[contains(text(), 'Submit application')]",
            "//button[contains(text(), 'Submit')]",
            "//button[contains(text(), 'Send application')]",
            "//input[@type='submit']"
        ]

        for selector in submit_selectors:
            try:
                if selector.startswith("//"):
                    button = self.driver.find_element(By.XPATH, selector)
                else:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)

                if button and button.is_displayed() and button.is_enabled():
                    return button
            except:
                continue

        return None

    def find_next_button(self):
        """Find next/continue button"""
        next_selectors = [
            "//button[contains(text(), 'Next')]",
            "//button[contains(text(), 'Continue')]",
            "//button[contains(@aria-label, 'Continue')]",
            "//button[contains(text(), 'Review')]"
        ]

        for selector in next_selectors:
            try:
                button = self.driver.find_element(By.XPATH, selector)
                if button and button.is_displayed() and button.is_enabled():
                    return button
            except:
                continue

        return None

    def go_to_next_page(self):
        """Navigate to next page of job results"""
        try:
            next_page_selectors = [
                "//button[@aria-label='View next page']",
                "//button[contains(text(), 'Next')]",
                ".artdeco-pagination__button--next"
            ]

            for selector in next_page_selectors:
                try:
                    if selector.startswith("//"):
                        next_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, selector)

                    if next_button and next_button.is_displayed() and next_button.is_enabled():
                        next_button.click()
                        print("📄 Moving to next page...")
                        self.human_delay(5, 8)
                        return True
                except:
                    continue

            print("📄 No more pages available")
            return False

        except Exception as e:
            print(f"❌ Error navigating to next page: {e}")
            return False

    def run(self):
        """Main execution with Ollama-enhanced job application"""
        print("🚀 Ollama-Enhanced LinkedIn Job Applier Starting...")
        print("=" * 60)
        print(f"👤 User: {self.profile['personal_info']['full_name']}")
        print(f"📧 Email: {self.email}")
        print(f"🔍 Search: {self.keywords} in {self.location}")
        print(f"🎯 Target: {self.max_applications} applications")
        print(f"🧠 Ollama: {'✅ Available' if self.ollama_available else '❌ Not Available'}")
        print("=" * 60)

        try:
            self.driver.maximize_window()

            # Step 1: Login
            print("\n🔐 Step 1: Logging into LinkedIn...")
            if not self.login_linkedin():
                print("❌ Login failed - stopping automation")
                return

            # Step 2: Navigate and search
            print("\n🔍 Step 2: Performing job search...")
            if not self.navigate_to_jobs_and_search():
                print("❌ Job search failed - stopping automation")
                return

            # Step 3: Start job applications
            print(f"\n🚀 Step 3: Starting Ollama-enhanced job applications...")
            print("=" * 60)

            # Main application loop
            page_number = 1
            consecutive_failures = 0
            max_consecutive_failures = 5

            while self.applications_sent < self.max_applications:
                print(f"\n📄 Processing page {page_number}...")

                # Get job listings
                job_listings = self.get_job_listings()

                if not job_listings:
                    print("❌ No job listings found")
                    consecutive_failures += 1

                    if consecutive_failures >= max_consecutive_failures:
                        print("❌ Too many failures, stopping...")
                        break

                    if not self.go_to_next_page():
                        break

                    page_number += 1
                    continue

                consecutive_failures = 0
                print(f"✅ Found {len(job_listings)} job listings")

                # Apply to each job with Ollama enhancement
                for i, job_listing in enumerate(job_listings):
                    if self.applications_sent >= self.max_applications:
                        print(f"🎯 Reached maximum applications ({self.max_applications})")
                        break

                    print(f"\n📋 Job {i+1}/{len(job_listings)} on page {page_number}")

                    try:
                        success = self.apply_to_job_enhanced(job_listing)

                        if success:
                            print(f"✅ Application successful! Total: {self.applications_sent}/{self.max_applications}")
                        else:
                            print("❌ Application failed or skipped")

                        # Human-like delay between applications
                        self.human_delay(5, 10)

                    except Exception as e:
                        print(f"❌ Error processing job: {e}")
                        continue

                # Go to next page if needed
                if self.applications_sent < self.max_applications:
                    if not self.go_to_next_page():
                        break
                    page_number += 1
                else:
                    break

            # Final summary
            self.print_final_summary()

        except KeyboardInterrupt:
            print("\n⚠️ Process interrupted by user")
            print(f"📊 Applications sent: {self.applications_sent}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print(f"📊 Applications sent: {self.applications_sent}")
        finally:
            print("\n👋 Closing browser...")
            self.driver.quit()

    def print_final_summary(self):
        """Print final application summary"""
        print("\n" + "=" * 60)
        print("🎉 OLLAMA-ENHANCED JOB APPLICATION COMPLETE!")
        print("=" * 60)
        print(f"👤 Applicant: {self.profile['personal_info']['full_name']}")
        print(f"🔍 Search Criteria: {self.keywords} in {self.location}")
        print(f"📊 Applications Sent: {self.applications_sent}")
        print(f"🎯 Target Applications: {self.max_applications}")
        print(f"🧠 Ollama Enhancement: {'✅ Used' if self.ollama_available else '❌ Not Available'}")

        if self.max_applications > 0:
            success_rate = (self.applications_sent / self.max_applications) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")

        if self.applications_sent > 0:
            print("\n✅ NEXT STEPS:")
            print("1. Monitor your email for application responses")
            print("2. Check LinkedIn messages for recruiter contacts")
            print("3. Prepare for potential interviews")

        print("=" * 60)

if __name__ == '__main__':
    print("🚀 Ollama-Enhanced LinkedIn Job Applier")
    print("🧠 Intelligent job application with local AI")
    print("=" * 60)

    try:
        applier = OllamaLinkedInApplier("user_profile.json")
        applier.run()
    except FileNotFoundError:
        print("❌ user_profile.json not found!")
        print("📝 Please create your user profile file first")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
