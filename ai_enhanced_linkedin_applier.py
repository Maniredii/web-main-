#!/usr/bin/env python3
"""
🤖 AI-Enhanced LinkedIn Auto Applier
Integrates Groq AI for intelligent automation and adaptability
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import json
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import base64
import requests
import threading

class AIEnhancedLinkedInApplier:
    def __init__(self, config=None):
        """Initialize with AI capabilities"""
        load_dotenv()
        
        # Credentials
        self.email = "tivep27728@devdigs.com"
        self.password = "Mani!8897"
        
        # AI Configuration - Fix the key name
        self.groq_api_key = os.getenv('GROK_API_KEY', '') or os.getenv('GROQ_API_KEY', '')
        self.use_ai = bool(self.groq_api_key)
        
        if config:
            self.keywords = config.get('keywords', 'Python Developer')
            self.location = config.get('location', 'Remote')
            self.max_applications = config.get('max_applications', 25)
        else:
            self.keywords = 'Python Developer'
            self.location = 'Remote'
            self.max_applications = 25
            
        self.applications_sent = 0
        
        print(f"🔐 Using credentials: {self.email}")
        print(f"🔍 Searching for: {self.keywords} in {self.location}")
        print(f"🎯 Max applications: {self.max_applications}")
        print(f"🤖 AI Enhancement: {'Enabled' if self.use_ai else 'Disabled'}")
        
        # Setup Chrome
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 10)

    def ai_analyze_page(self, task_description):
        """Use AI to analyze current page and suggest actions"""
        if not self.use_ai:
            return None
        
        try:
            # Get page screenshot and HTML
            screenshot_path = "temp_screenshot.png"
            self.driver.save_screenshot(screenshot_path)
            
            # Get page source (truncated for API)
            page_source = self.driver.page_source[:5000]  # Limit for API
            current_url = self.driver.current_url
            
            # Prepare AI prompt
            prompt = f"""
You are an expert LinkedIn automation assistant. Analyze the current page and provide guidance.

Task: {task_description}
Current URL: {current_url}
Page HTML (first 5000 chars): {page_source}

Please analyze and provide:
1. What type of page this is (login, jobs, profile, etc.)
2. What actions should be taken next
3. Any potential issues or challenges detected
4. Specific CSS selectors or XPath expressions for key elements
5. Whether manual intervention might be needed

Respond in JSON format:
{{
    "page_type": "string",
    "recommended_actions": ["action1", "action2"],
    "potential_issues": ["issue1", "issue2"],
    "key_selectors": {{"element_name": "selector"}},
    "manual_intervention_needed": boolean,
    "confidence": 0.0-1.0
}}
"""
            
            # Call Groq API
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-8b-8192",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 1000
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                content = ai_response['choices'][0]['message']['content']
                
                # Try to parse JSON response
                try:
                    analysis = json.loads(content)
                    print(f"🤖 AI Analysis: {analysis.get('page_type', 'Unknown')} page")
                    print(f"🎯 Confidence: {analysis.get('confidence', 0):.1%}")
                    return analysis
                except json.JSONDecodeError:
                    print(f"🤖 AI Response: {content}")
                    return {"raw_response": content}
            
            # Clean up
            try:
                os.remove(screenshot_path)
            except:
                pass
                
        except Exception as e:
            print(f"⚠️ AI analysis failed: {e}")
        
        return None

    def ai_find_elements(self, element_description):
        """Use AI to find elements on the page"""
        if not self.use_ai:
            return []
        
        try:
            page_source = self.driver.page_source[:3000]
            
            prompt = f"""
Find CSS selectors or XPath expressions for: {element_description}

Page HTML (partial): {page_source}

Return only the most reliable selectors in JSON format:
{{
    "selectors": ["selector1", "selector2", "selector3"],
    "confidence": 0.0-1.0
}}
"""
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-8b-8192",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                content = ai_response['choices'][0]['message']['content']
                
                try:
                    result = json.loads(content)
                    selectors = result.get('selectors', [])
                    print(f"🤖 AI found {len(selectors)} selectors for: {element_description}")
                    return selectors
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️ AI element finding failed: {e}")
        
        return []

    def smart_find_element(self, element_description, fallback_selectors=None):
        """Intelligently find elements using AI + fallback selectors"""
        all_selectors = []
        
        # Get AI suggestions first
        if self.use_ai:
            ai_selectors = self.ai_find_elements(element_description)
            all_selectors.extend(ai_selectors)
        
        # Add fallback selectors
        if fallback_selectors:
            all_selectors.extend(fallback_selectors)
        
        # Try each selector
        for selector in all_selectors:
            try:
                if selector.startswith("//"):
                    element = self.driver.find_element(By.XPATH, selector)
                else:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                if element and element.is_displayed():
                    print(f"✅ Found element using: {selector}")
                    return element
            except:
                continue
        
        print(f"❌ Could not find: {element_description}")
        return None

    def human_delay(self, min_sec=1, max_sec=3):
        """Human-like random delays"""
        time.sleep(random.uniform(min_sec, max_sec))

    def type_like_human(self, element, text):
        """Type with human-like delays"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    def show_manual_intervention_popup(self, title, message, instructions=""):
        """Show GUARANTEED manual intervention popup"""
        print(f"\n🚨 MANUAL INTERVENTION REQUIRED: {title}")
        print("=" * 60)
        print(f"📋 {message}")
        if instructions:
            print(f"💡 {instructions}")
        print("=" * 60)

        # Method 1: Simple messagebox (most reliable)
        try:
            print("🔔 Showing popup window...")

            # Create new root window
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            root.lift()
            root.focus_force()

            # Combine message and instructions
            full_message = f"{message}\n\n{instructions}" if instructions else message

            # Show messagebox with attention-grabbing title
            messagebox.showinfo(
                "🚨 LINKEDIN AUTOMATION - MANUAL ACTION REQUIRED 🚨",
                full_message
            )

            root.destroy()
            print("✅ User completed manual intervention!")
            return True

        except Exception as e:
            print(f"⚠️ Popup failed: {e}")

        # Method 2: Terminal fallback (always works)
        print("\n" + "🔴" * 30)
        print("🚨 POPUP FAILED - USING TERMINAL")
        print("🔴" * 30)
        print(f"📋 {message}")
        if instructions:
            print(f"💡 {instructions}")
        print("🔴" * 30)
        print("⌨️ Press ENTER after completing the action...")
        print("🔴" * 30)

        try:
            input()
            print("✅ User confirmed via terminal!")
            return True
        except:
            print("❌ User cancelled")
            return False





    def detect_manual_intervention_needed(self):
        """AI-enhanced detection of manual intervention needs"""
        current_url = self.driver.current_url.lower()
        page_source = self.driver.page_source.lower()

        # Use AI analysis if available
        if self.use_ai:
            analysis = self.ai_analyze_page("Detect if manual intervention is needed")
            if analysis and analysis.get('manual_intervention_needed'):
                intervention_type = analysis.get('page_type', 'unknown')
                return self.show_manual_intervention_popup(
                    f"🤖 AI Detected: {intervention_type.title()}",
                    "AI has detected that manual intervention is required.\n\nPlease complete the required action in the browser.",
                    "Follow the instructions on screen, then click 'Continue Automation'"
                )

        # Fallback to traditional detection
        interventions = {
            'captcha': {
                'indicators': ['captcha', 'recaptcha', 'verify you are human', 'security check'],
                'title': '🤖 CAPTCHA Detected',
                'message': 'LinkedIn is asking you to complete a CAPTCHA puzzle.\n\nPlease solve the CAPTCHA in the browser window.',
                'instructions': 'Click "Continue Automation" after completing the CAPTCHA'
            },
            'security_challenge': {
                'indicators': ['challenge', 'security', 'verify', 'suspicious activity'],
                'title': '🔒 Security Challenge',
                'message': 'LinkedIn has detected unusual activity.\n\nPlease complete the security challenge.',
                'instructions': 'Follow LinkedIn\'s instructions, then click "Continue Automation"'
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
        """AI-enhanced LinkedIn login"""
        print(f"🔐 Logging into LinkedIn with AI assistance...")

        try:
            self.driver.get("https://www.linkedin.com/login")
            self.human_delay(2, 4)

            # Use AI to find email field
            email_field = self.smart_find_element(
                "email input field for login",
                ["input[name='session_key']", "#username", "input[type='email']"]
            )

            if email_field:
                email_field.clear()
                self.type_like_human(email_field, self.email)
                print(f"✅ Email entered: {self.email}")
            else:
                print("❌ Could not find email field")
                return False

            # Use AI to find password field
            password_field = self.smart_find_element(
                "password input field for login",
                ["input[name='session_password']", "#password", "input[type='password']"]
            )

            if password_field:
                password_field.clear()
                self.type_like_human(password_field, self.password)
                print("✅ Password entered")
            else:
                print("❌ Could not find password field")
                return False

            # Submit login
            password_field.send_keys(Keys.RETURN)
            self.human_delay(3, 5)

            # Check login result with AI assistance
            for attempt in range(3):
                current_url = self.driver.current_url.lower()
                print(f"📍 Login attempt {attempt + 1}: {current_url}")

                # Use AI to analyze login result
                if self.use_ai:
                    analysis = self.ai_analyze_page("Check if login was successful")
                    if analysis:
                        page_type = analysis.get('page_type', '').lower()
                        if 'feed' in page_type or 'dashboard' in page_type or 'home' in page_type:
                            print("✅ AI confirmed: Login successful!")
                            return True

                # Fallback checks
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

    def navigate_to_jobs(self):
        """AI-enhanced navigation to Jobs section"""
        print("🧭 AI-enhanced navigation to Jobs section...")

        try:
            # Use AI to analyze current page and suggest navigation
            if self.use_ai:
                analysis = self.ai_analyze_page("Navigate to LinkedIn Jobs section")
                if analysis:
                    recommended_actions = analysis.get('recommended_actions', [])
                    print(f"🤖 AI recommendations: {recommended_actions}")

            # Method 1: Direct URL
            self.driver.get("https://www.linkedin.com/jobs/")
            self.human_delay(3, 5)

            current_url = self.driver.current_url.lower()
            if "jobs" in current_url:
                print("✅ Successfully navigated to Jobs section!")
                return True

            # Method 2: AI-assisted Jobs tab finding
            jobs_link = self.smart_find_element(
                "Jobs navigation link or tab",
                [
                    "//a[contains(@href, '/jobs')]",
                    "//a[contains(text(), 'Jobs')]",
                    "[data-control-name='nav.jobs']",
                    ".global-nav__primary-link[href*='jobs']"
                ]
            )

            if jobs_link:
                jobs_link.click()
                self.human_delay(3, 5)

                current_url = self.driver.current_url.lower()
                if "jobs" in current_url:
                    print("✅ AI-assisted navigation successful!")
                    return True

            print("❌ Failed to navigate to Jobs section")
            return False

        except Exception as e:
            print(f"❌ Navigation error: {e}")
            return False

    def search_jobs(self):
        """AI-enhanced job search"""
        print(f"🔍 AI-enhanced search for '{self.keywords}' in '{self.location}'...")

        try:
            # Use AI to find search elements
            keyword_box = self.smart_find_element(
                "job search keyword input field",
                [
                    "input[aria-label*='Search jobs']",
                    "input[placeholder*='Search jobs']",
                    ".jobs-search-box__text-input[aria-label*='Search jobs']"
                ]
            )

            if keyword_box:
                keyword_box.clear()
                self.type_like_human(keyword_box, self.keywords)
                print(f"✅ Keywords entered: {self.keywords}")

            location_box = self.smart_find_element(
                "job search location input field",
                [
                    "input[aria-label*='Search location']",
                    "input[placeholder*='Search location']",
                    ".jobs-search-box__text-input[aria-label*='location']"
                ]
            )

            if location_box:
                location_box.clear()
                self.type_like_human(location_box, self.location)
                print(f"✅ Location entered: {self.location}")

            # Submit search
            if keyword_box:
                keyword_box.send_keys(Keys.RETURN)
            elif location_box:
                location_box.send_keys(Keys.RETURN)

            print("✅ AI-enhanced search submitted!")
            self.human_delay(3, 5)
            return True

        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False

    def get_job_listings(self):
        """Get job listings from current page"""
        try:
            # Use AI to find job listings if available
            if self.use_ai:
                job_elements = self.smart_find_elements(
                    "job listing cards or items on the page",
                    [
                        ".jobs-search-results__list-item",
                        ".job-card-container",
                        "[data-job-id]",
                        ".scaffold-layout__list-item",
                        ".jobs-search-results-list__item"
                    ]
                )
            else:
                # Fallback selectors
                selectors = [
                    ".jobs-search-results__list-item",
                    ".job-card-container",
                    "[data-job-id]",
                    ".scaffold-layout__list-item",
                    ".jobs-search-results-list__item"
                ]

                job_elements = []
                for selector in selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            job_elements = elements
                            print(f"✅ Found {len(elements)} jobs using: {selector}")
                            break
                    except:
                        continue

            return job_elements

        except Exception as e:
            print(f"❌ Error getting job listings: {e}")
            return []

    def smart_find_elements(self, description, fallback_selectors):
        """Find multiple elements using AI + fallback"""
        all_selectors = []

        # Get AI suggestions
        if self.use_ai:
            ai_selectors = self.ai_find_elements(description)
            all_selectors.extend(ai_selectors)

        # Add fallback selectors
        all_selectors.extend(fallback_selectors)

        # Try each selector
        for selector in all_selectors:
            try:
                if selector.startswith("//"):
                    elements = self.driver.find_elements(By.XPATH, selector)
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                if elements:
                    print(f"✅ Found {len(elements)} elements using: {selector}")
                    return elements
            except:
                continue

        print(f"❌ Could not find: {description}")
        return []

    def apply_to_job(self, job_element):
        """Apply to a single job"""
        try:
            # Scroll job into view and click
            self.driver.execute_script("arguments[0].scrollIntoView(true);", job_element)
            self.human_delay(1, 2)

            # Click on the job listing
            job_element.click()
            self.human_delay(2, 3)

            # Check for manual intervention
            if self.detect_manual_intervention_needed():
                return False

            # Get job title for logging
            try:
                job_title_selectors = [
                    "h1",
                    ".job-details-jobs-unified-top-card__job-title",
                    ".jobs-unified-top-card__job-title",
                    "[data-job-title]"
                ]

                job_title = "Unknown Position"
                for selector in job_title_selectors:
                    try:
                        title_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if title_element and title_element.text.strip():
                            job_title = title_element.text.strip()
                            break
                    except:
                        continue

                print(f"📝 Applying to: {job_title}")
            except:
                print("📝 Applying to job...")

            # Find Easy Apply button
            easy_apply_button = self.smart_find_element(
                "Easy Apply button for job application",
                [
                    "//button[contains(@aria-label, 'Easy Apply')]",
                    "//button[contains(text(), 'Easy Apply')]",
                    ".jobs-apply-button",
                    "[data-control-name='jobdetails_topcard_inapply']"
                ]
            )

            if not easy_apply_button:
                print("❌ No Easy Apply button found, skipping...")
                return False

            # Click Easy Apply
            easy_apply_button.click()
            self.human_delay(2, 3)

            # Check for manual intervention after clicking
            if self.detect_manual_intervention_needed():
                return False

            # Handle application process
            return self.complete_application()

        except Exception as e:
            print(f"❌ Error applying to job: {e}")
            return False

    def complete_application(self):
        """Complete the Easy Apply application process"""
        try:
            max_steps = 5  # Prevent infinite loops
            current_step = 0

            while current_step < max_steps:
                current_step += 1
                print(f"📋 Application step {current_step}...")

                # Check for manual intervention
                if self.detect_manual_intervention_needed():
                    return True  # Count as success since user will handle it

                # Look for submit button (final step)
                submit_selectors = [
                    "//button[contains(@aria-label, 'Submit application')]",
                    "//button[contains(text(), 'Submit application')]",
                    "//button[contains(text(), 'Submit')]",
                    "[data-control-name='continue_unify']"
                ]

                submit_button = None
                for selector in submit_selectors:
                    try:
                        if selector.startswith("//"):
                            submit_button = self.driver.find_element(By.XPATH, selector)
                        else:
                            submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)

                        if submit_button and submit_button.is_displayed() and submit_button.is_enabled():
                            break
                    except:
                        continue

                if submit_button:
                    submit_button.click()
                    print("✅ Application submitted!")
                    self.applications_sent += 1
                    self.human_delay(2, 3)
                    return True

                # Look for Next/Continue button
                next_selectors = [
                    "//button[contains(text(), 'Next')]",
                    "//button[contains(text(), 'Continue')]",
                    "//button[contains(@aria-label, 'Continue')]",
                    "[data-control-name='continue_unify']"
                ]

                next_button = None
                for selector in next_selectors:
                    try:
                        if selector.startswith("//"):
                            next_button = self.driver.find_element(By.XPATH, selector)
                        else:
                            next_button = self.driver.find_element(By.CSS_SELECTOR, selector)

                        if next_button and next_button.is_displayed() and next_button.is_enabled():
                            break
                    except:
                        continue

                if next_button:
                    next_button.click()
                    self.human_delay(2, 3)
                    continue

                # If no next or submit button, might be complex application
                print("⚠️ Complex application detected - may require manual completion")
                if self.show_manual_intervention_popup(
                    "📝 Complex Application",
                    "This job application requires additional information or has multiple steps.\n\nPlease complete the application manually in the browser.",
                    "Fill out all required fields and submit, then click 'OK' to continue automation"
                ):
                    return True  # Count as success
                else:
                    return False

            print("⚠️ Application process exceeded maximum steps")
            return False

        except Exception as e:
            print(f"❌ Error completing application: {e}")
            return False

    def close_modal(self):
        """Close any open modals or popups"""
        try:
            close_selectors = [
                "//button[@aria-label='Dismiss']",
                "//button[contains(text(), 'Discard')]",
                ".artdeco-modal__dismiss",
                "[data-control-name='overlay.close_button']"
            ]

            for selector in close_selectors:
                try:
                    if selector.startswith("//"):
                        close_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        close_button = self.driver.find_element(By.CSS_SELECTOR, selector)

                    if close_button and close_button.is_displayed():
                        close_button.click()
                        self.human_delay(1, 2)
                        return True
                except:
                    continue

            return False
        except:
            return False

    def go_to_next_page(self):
        """Navigate to next page of job results"""
        try:
            next_page_selectors = [
                "//button[@aria-label='View next page']",
                "//button[contains(text(), 'Next')]",
                ".artdeco-pagination__button--next",
                "[data-control-name='pagination-next']"
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
                        self.human_delay(3, 5)
                        return True
                except:
                    continue

            print("📄 No more pages available")
            return False

        except Exception as e:
            print(f"❌ Error navigating to next page: {e}")
            return False

    def run(self):
        """Main AI-enhanced execution with complete job application process"""
        print("🤖 AI-Enhanced LinkedIn Auto Applier Starting...")
        print("=" * 60)

        if self.use_ai:
            print("🧠 AI Enhancement: ACTIVE")
            print("🔗 Using Groq API for intelligent automation")
        else:
            print("⚠️ AI Enhancement: DISABLED (No API key)")
            print("🔧 Falling back to traditional automation")

        print("=" * 60)

        try:
            self.driver.maximize_window()

            # AI-enhanced login
            if not self.login_linkedin():
                print("❌ Login failed")
                return

            # AI-enhanced navigation
            if not self.navigate_to_jobs():
                print("❌ Navigation failed")
                return

            # AI-enhanced job search
            if not self.search_jobs():
                print("❌ Search failed")
                return

            # Apply Easy Apply filter
            current_url = self.driver.current_url
            if "f_LF=f_AL" not in current_url:
                separator = "&" if "?" in current_url else "?"
                new_url = f"{current_url}{separator}f_LF=f_AL"
                self.driver.get(new_url)
                self.human_delay(3, 5)
                print("✅ Easy Apply filter applied!")

            print(f"\n🚀 Starting Job Application Process...")
            print(f"🎯 Target: {self.max_applications} applications")
            print(f"🔍 Keywords: {self.keywords}")
            print(f"📍 Location: {self.location}")
            print("=" * 60)

            # Main application loop
            page_number = 1
            consecutive_failures = 0
            max_consecutive_failures = 5

            while self.applications_sent < self.max_applications:
                print(f"\n📄 Processing page {page_number}...")

                # Get job listings on current page
                job_listings = self.get_job_listings()

                if not job_listings:
                    print("❌ No job listings found on this page")
                    consecutive_failures += 1

                    if consecutive_failures >= max_consecutive_failures:
                        print("❌ Too many consecutive failures, stopping...")
                        break

                    # Try next page
                    if not self.go_to_next_page():
                        print("❌ No more pages available")
                        break

                    page_number += 1
                    continue

                consecutive_failures = 0  # Reset failure counter
                print(f"✅ Found {len(job_listings)} job listings")

                # Apply to each job on current page
                for i, job_listing in enumerate(job_listings):
                    if self.applications_sent >= self.max_applications:
                        print(f"🎯 Reached maximum applications ({self.max_applications})")
                        break

                    print(f"\n📋 Job {i+1}/{len(job_listings)} on page {page_number}")

                    try:
                        success = self.apply_to_job(job_listing)

                        if success:
                            print(f"✅ Application successful! Total: {self.applications_sent}/{self.max_applications}")
                        else:
                            print("❌ Application failed or skipped")

                        # Human-like delay between applications
                        self.human_delay(3, 8)

                    except Exception as e:
                        print(f"❌ Error processing job: {e}")
                        continue

                # Check if we need to continue to next page
                if self.applications_sent < self.max_applications:
                    if not self.go_to_next_page():
                        print("📄 No more pages available")
                        break
                    page_number += 1
                else:
                    break

            # Final summary
            print("\n" + "=" * 60)
            print("🎉 Job Application Process Complete!")
            print(f"📊 Total applications sent: {self.applications_sent}")
            print(f"🎯 Target was: {self.max_applications}")
            print(f"📈 Success rate: {(self.applications_sent/self.max_applications)*100:.1f}%")
            print("=" * 60)

        except KeyboardInterrupt:
            print("\n⚠️ Process interrupted by user")
            print(f"📊 Applications sent before interruption: {self.applications_sent}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print(f"📊 Applications sent before error: {self.applications_sent}")
        finally:
            print("\n👋 Closing browser...")
            self.driver.quit()

if __name__ == '__main__':
    print("🤖 AI-Enhanced LinkedIn Auto Applier")
    print("🧠 Powered by Groq AI for intelligent automation")
    print("=" * 60)

    # Check for Groq API key
    load_dotenv()
    groq_key = os.getenv('GROK_API_KEY', '') or os.getenv('GROQ_API_KEY', '')

    if groq_key:
        print(f"✅ AI API Key found: {groq_key[:10]}...")
        print("🧠 AI Enhancement: ENABLED")
    else:
        print("⚠️ No GROK_API_KEY found in .env file")
        print("🔧 Add GROK_API_KEY=your_key_here to .env for AI features")
        print("📝 Get free API key at: https://console.groq.com/")
        print("🚀 Continuing with traditional automation...")

    config = None
    try:
        with open('linkedin_config.json') as f:
            config = json.load(f)
        print("✅ Config loaded")
    except:
        print("ℹ️ Using defaults")

    try:
        applier = AIEnhancedLinkedInApplier(config)
        applier.run()
    except Exception as e:
        print(f"❌ Error: {e}")
