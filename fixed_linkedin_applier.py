#!/usr/bin/env python3
"""
🚀 Fixed LinkedIn Job Applier
Properly clicks Easy Apply buttons without triggering popups
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
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
import requests

class FixedLinkedInApplier:
    def __init__(self, profile_path="user_profile.json"):
        """Initialize with user profile"""
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
        
        # Setup Ollama (optional)
        self.setup_ollama()
        
        # Setup Chrome with enhanced stealth
        self.setup_chrome_driver()

    def setup_ollama(self):
        """Setup Ollama if available"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                models = result.stdout.strip()
                if 'qwen2.5:7b' in models:
                    self.ollama_model = "qwen2.5:7b"
                elif 'llama3.1:8b' in models:
                    self.ollama_model = "llama3.1:8b"
                elif models and 'NAME' in models:
                    lines = models.split('\n')[1:]
                    if lines:
                        self.ollama_model = lines[0].split()[0]
                    else:
                        self.ollama_model = None
                else:
                    self.ollama_model = None
                
                if self.ollama_model:
                    print(f"🧠 Ollama available: {self.ollama_model}")
                    self.ollama_available = True
                else:
                    print("⚠️ No Ollama models found")
                    self.ollama_available = False
            else:
                self.ollama_available = False
        except:
            self.ollama_available = False

    def setup_chrome_driver(self):
        """Setup Chrome driver with enhanced stealth features"""
        chrome_options = Options()
        
        # Enhanced stealth options
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Realistic user agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Additional stealth options
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Faster loading
        
        # Window size
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute stealth scripts
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
        
        self.wait = WebDriverWait(self.driver, 15)
        self.actions = ActionChains(self.driver)

    def human_delay(self, min_sec=2, max_sec=5):
        """More realistic human delays"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def type_like_human(self, element, text, clear_first=True):
        """Type with very human-like behavior"""
        if clear_first:
            element.clear()
            self.human_delay(0.5, 1)
        
        for char in text:
            element.send_keys(char)
            # Vary typing speed
            if random.random() < 0.1:  # 10% chance of longer pause
                time.sleep(random.uniform(0.2, 0.5))
            else:
                time.sleep(random.uniform(0.05, 0.15))

    def scroll_to_element_smoothly(self, element):
        """Scroll to element with smooth human-like scrolling"""
        try:
            # Get element location
            location = element.location_once_scrolled_into_view
            
            # Scroll with JavaScript for smooth scrolling
            self.driver.execute_script("""
                arguments[0].scrollIntoView({
                    behavior: 'smooth',
                    block: 'center',
                    inline: 'nearest'
                });
            """, element)
            
            self.human_delay(1, 2)
            return True
        except Exception as e:
            print(f"⚠️ Scroll error: {e}")
            return False

    def click_element_safely(self, element, method="click"):
        """Click element with multiple fallback methods"""
        try:
            # Method 1: Scroll into view first
            self.scroll_to_element_smoothly(element)
            
            # Method 2: Wait for element to be clickable
            self.wait.until(EC.element_to_be_clickable(element))
            
            # Method 3: Try different click methods
            if method == "click":
                element.click()
            elif method == "js_click":
                self.driver.execute_script("arguments[0].click();", element)
            elif method == "action_click":
                self.actions.move_to_element(element).click().perform()
            
            print(f"✅ Successfully clicked element using {method}")
            return True
            
        except ElementClickInterceptedException:
            print("⚠️ Click intercepted, trying JavaScript click...")
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except:
                return False
        except Exception as e:
            print(f"⚠️ Click failed with {method}: {e}")
            return False

    def show_manual_intervention_popup(self, title, message, instructions=""):
        """Show manual intervention popup"""
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
        
        # Check for various intervention scenarios
        interventions = [
            ('captcha', 'recaptcha', 'verify you are human', 'security check'),
            ('challenge', 'security', 'verify', 'suspicious activity'),
            ('two-factor', '2fa', 'verification code', 'enter code'),
            ('blocked', 'restricted', 'temporarily unavailable')
        ]
        
        for indicators in interventions:
            for indicator in indicators:
                if indicator in current_url or indicator in page_source:
                    return self.show_manual_intervention_popup(
                        "🔒 Manual Action Required",
                        f"LinkedIn requires manual action: {indicator}",
                        "Please complete the required action in the browser, then click OK to continue"
                    )
        
        return False

    def login_linkedin(self):
        """Enhanced LinkedIn login"""
        print(f"🔐 Logging into LinkedIn...")
        
        try:
            self.driver.get("https://www.linkedin.com/login")
            self.human_delay(3, 5)

            # Enter email with human-like behavior
            email_field = self.wait.until(EC.presence_of_element_located((By.NAME, 'session_key')))
            self.type_like_human(email_field, self.email)
            print(f"✅ Email entered")
            self.human_delay(1, 3)

            # Enter password
            password_field = self.driver.find_element(By.NAME, 'session_password')
            self.type_like_human(password_field, self.password)
            print("✅ Password entered")
            self.human_delay(2, 4)

            # Submit login with human-like behavior
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            self.click_element_safely(login_button)
            self.human_delay(5, 8)
            
            # Check login success
            for attempt in range(5):
                current_url = self.driver.current_url.lower()
                print(f"📍 Login check {attempt + 1}: {current_url}")
                
                if any(indicator in current_url for indicator in ["feed", "/in/", "jobs"]):
                    print("✅ Login successful!")
                    return True
                
                if self.detect_manual_intervention_needed():
                    self.human_delay(3, 5)
                    continue
                
                if "login" in current_url or "challenge" in current_url:
                    print("⚠️ Login may have failed or requires verification")
                    if attempt < 4:  # Not last attempt
                        self.human_delay(3, 5)
                        continue
                    else:
                        return False
                
                self.human_delay(3, 5)
            
            return False
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False

    def navigate_to_jobs_and_search(self):
        """Navigate to jobs and perform search"""
        print("🧭 Navigating to Jobs section...")

        try:
            # Direct URL navigation with Easy Apply filter
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={self.keywords.replace(' ', '%20')}&location={self.location.replace(' ', '%20')}&f_LF=f_AL"
            print(f"🔍 Navigating to: {search_url}")

            self.driver.get(search_url)
            self.human_delay(5, 8)

            # Verify we're on jobs page
            current_url = self.driver.current_url.lower()
            if "jobs" in current_url:
                print("✅ Successfully navigated to jobs page")
                return self.verify_search_results()

            return False

        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False

    def verify_search_results(self):
        """Verify search results are displayed"""
        try:
            print("🔍 Verifying search results...")
            self.human_delay(3, 5)

            result_selectors = [
                ".jobs-search-results__list-item",
                ".job-card-container",
                "[data-job-id]"
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
                "[data-job-id]"
            ]

            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ Found {len(elements)} job listings")
                        return elements
                except:
                    continue

            return []

        except Exception as e:
            print(f"❌ Error getting job listings: {e}")
            return []

    def find_easy_apply_button_fixed(self):
        """Fixed Easy Apply button detection"""
        print("🔍 Looking for Easy Apply button...")

        # Wait for page to load
        self.human_delay(2, 3)

        # Enhanced selectors
        selectors = [
            "//button[contains(@aria-label, 'Easy Apply to')]",
            "//button[contains(@aria-label, 'Easy Apply')]",
            "//button[contains(text(), 'Easy Apply')]",
            "//span[contains(text(), 'Easy Apply')]/parent::button",
            ".jobs-apply-button",
            "//button[contains(@class, 'jobs-apply-button')]"
        ]

        for i, selector in enumerate(selectors, 1):
            try:
                print(f"🔍 Trying selector {i}...")

                if selector.startswith("//"):
                    elements = self.driver.find_elements(By.XPATH, selector)
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                for element in elements:
                    try:
                        if element.is_displayed() and element.is_enabled():
                            text = element.text.lower()
                            aria_label = element.get_attribute('aria-label') or ""

                            if 'easy apply' in text or 'easy apply' in aria_label.lower():
                                print(f"✅ Found Easy Apply button!")
                                return element
                    except:
                        continue

            except Exception as e:
                print(f"⚠️ Selector {i} failed: {e}")
                continue

        print("❌ No Easy Apply button found")
        return None

    def apply_to_job_fixed(self, job_element):
        """Fixed job application process"""
        try:
            print(f"\n📋 Processing job application...")

            # Click job listing
            self.scroll_to_element_smoothly(job_element)
            self.human_delay(1, 2)

            # Try clicking the job
            if not self.click_element_safely(job_element):
                print("❌ Failed to click job listing")
                return False

            self.human_delay(3, 5)

            # Check for manual intervention
            if self.detect_manual_intervention_needed():
                return False

            # Extract job info
            job_info = self.extract_job_info()
            print(f"📝 Job: {job_info['title']} at {job_info['company']}")

            # Find Easy Apply button
            easy_apply_button = self.find_easy_apply_button_fixed()

            if not easy_apply_button:
                print("❌ No Easy Apply button found, skipping...")
                return False

            # Click Easy Apply with enhanced reliability
            print("🎯 Clicking Easy Apply button...")

            # Multiple click attempts with different methods
            for attempt in range(3):
                print(f"🔄 Click attempt {attempt + 1}...")

                # Try different click methods
                methods = ["click", "js_click", "action_click"]
                for method in methods:
                    try:
                        if self.click_element_safely(easy_apply_button, method):
                            print("✅ Easy Apply button clicked successfully!")
                            self.human_delay(3, 5)

                            # Check if application form opened
                            if self.check_application_form_opened():
                                return self.complete_application_fixed(job_info)
                            else:
                                print("⚠️ Application form didn't open, trying again...")
                                break
                    except Exception as e:
                        print(f"⚠️ Click method {method} failed: {e}")
                        continue

                self.human_delay(2, 3)

            print("❌ Failed to click Easy Apply button after all attempts")
            return False

        except Exception as e:
            print(f"❌ Error in job application: {e}")
            return False

    def check_application_form_opened(self):
        """Check if application form opened after clicking Easy Apply"""
        try:
            # Look for application form indicators
            form_indicators = [
                ".jobs-easy-apply-modal",
                ".artdeco-modal",
                "//h3[contains(text(), 'Submit application')]",
                "//button[contains(text(), 'Submit application')]",
                "//button[contains(text(), 'Next')]"
            ]

            for indicator in form_indicators:
                try:
                    if indicator.startswith("//"):
                        element = self.driver.find_element(By.XPATH, indicator)
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, indicator)

                    if element and element.is_displayed():
                        print("✅ Application form opened!")
                        return True
                except:
                    continue

            print("⚠️ Application form not detected")
            return False

        except Exception as e:
            print(f"⚠️ Error checking form: {e}")
            return False

    def extract_job_info(self):
        """Extract job information"""
        job_info = {
            'title': 'Unknown Position',
            'company': 'Unknown Company'
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
                ".jobs-unified-top-card__company-name"
            ]

            for selector in company_selectors:
                try:
                    company_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if company_element and company_element.text.strip():
                        job_info['company'] = company_element.text.strip()
                        break
                except:
                    continue

        except Exception as e:
            print(f"⚠️ Error extracting job info: {e}")

        return job_info

    def complete_application_fixed(self, job_info):
        """Complete application with enhanced form handling"""
        try:
            max_steps = 5
            current_step = 0

            while current_step < max_steps:
                current_step += 1
                print(f"📋 Application step {current_step}...")

                # Check for manual intervention
                if self.detect_manual_intervention_needed():
                    return True

                # Fill form fields
                self.fill_application_form_basic()

                # Look for submit button
                submit_button = self.find_submit_button()

                if submit_button:
                    if self.click_element_safely(submit_button):
                        print("✅ Application submitted!")
                        self.applications_sent += 1
                        self.human_delay(3, 5)
                        return True

                # Look for Next/Continue button
                next_button = self.find_next_button()

                if next_button:
                    if self.click_element_safely(next_button):
                        self.human_delay(2, 3)
                        continue

                # Complex application
                print("⚠️ Complex application detected")
                if self.show_manual_intervention_popup(
                    "📝 Complex Application",
                    f"The application for {job_info['title']} at {job_info['company']} requires manual completion.\n\nPlease complete it in the browser.",
                    "Fill out all fields and submit, then click 'OK' to continue"
                ):
                    self.applications_sent += 1
                    return True
                else:
                    return False

            print("⚠️ Application exceeded maximum steps")
            return False

        except Exception as e:
            print(f"❌ Error completing application: {e}")
            return False

    def fill_application_form_basic(self):
        """Basic form filling with profile data"""
        try:
            # Find all input fields
            input_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email'], input[type='tel'], textarea")

            for field in input_fields:
                try:
                    if not field.is_displayed() or not field.is_enabled():
                        continue

                    # Get field information
                    field_name = field.get_attribute('name') or ""
                    field_id = field.get_attribute('id') or ""
                    placeholder = field.get_attribute('placeholder') or ""
                    aria_label = field.get_attribute('aria-label') or ""

                    field_info = f"{field_name} {field_id} {placeholder} {aria_label}".lower()

                    # Fill based on field type
                    value = None
                    if any(word in field_info for word in ['first', 'fname', 'given']):
                        value = self.profile['personal_info']['first_name']
                    elif any(word in field_info for word in ['last', 'lname', 'family', 'surname']):
                        value = self.profile['personal_info']['last_name']
                    elif 'email' in field_info:
                        value = self.profile['personal_info']['email']
                    elif 'phone' in field_info:
                        value = self.profile['personal_info']['phone']
                    elif any(word in field_info for word in ['salary', 'compensation']):
                        value = self.profile['application_responses']['salary_expectations']['range']
                    elif any(word in field_info for word in ['experience', 'years']):
                        value = "5+"

                    if value:
                        self.type_like_human(field, value)
                        print(f"✅ Filled field: {value}")
                        self.human_delay(0.5, 1)

                except Exception as e:
                    print(f"⚠️ Error filling field: {e}")
                    continue

        except Exception as e:
            print(f"⚠️ Error in form filling: {e}")

    def find_submit_button(self):
        """Find submit button"""
        submit_selectors = [
            "//button[contains(@aria-label, 'Submit application')]",
            "//button[contains(text(), 'Submit application')]",
            "//button[contains(text(), 'Submit')]",
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
            "//button[contains(@aria-label, 'Continue')]"
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
        """Navigate to next page"""
        try:
            next_selectors = [
                "//button[@aria-label='View next page']",
                "//button[contains(text(), 'Next')]",
                ".artdeco-pagination__button--next"
            ]

            for selector in next_selectors:
                try:
                    if selector.startswith("//"):
                        next_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, selector)

                    if next_button and next_button.is_displayed() and next_button.is_enabled():
                        if self.click_element_safely(next_button):
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
        """Main execution"""
        print("🚀 Fixed LinkedIn Job Applier Starting...")
        print("=" * 60)
        print(f"👤 User: {self.profile['personal_info']['full_name']}")
        print(f"📧 Email: {self.email}")
        print(f"🔍 Search: {self.keywords} in {self.location}")
        print(f"🎯 Target: {self.max_applications} applications")
        print("=" * 60)

        try:
            self.driver.maximize_window()

            # Step 1: Login
            print("\n🔐 Step 1: Logging into LinkedIn...")
            if not self.login_linkedin():
                print("❌ Login failed")
                return

            # Step 2: Navigate and search
            print("\n🔍 Step 2: Performing job search...")
            if not self.navigate_to_jobs_and_search():
                print("❌ Job search failed")
                return

            # Step 3: Apply to jobs
            print(f"\n🚀 Step 3: Starting job applications...")
            print("=" * 60)

            page_number = 1
            consecutive_failures = 0
            max_consecutive_failures = 5

            while self.applications_sent < self.max_applications:
                print(f"\n📄 Processing page {page_number}...")

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

                # Apply to each job
                for i, job_listing in enumerate(job_listings):
                    if self.applications_sent >= self.max_applications:
                        print(f"🎯 Reached maximum applications ({self.max_applications})")
                        break

                    print(f"\n📋 Job {i+1}/{len(job_listings)} on page {page_number}")

                    try:
                        success = self.apply_to_job_fixed(job_listing)

                        if success:
                            print(f"✅ Application successful! Total: {self.applications_sent}/{self.max_applications}")
                        else:
                            print("❌ Application failed or skipped")

                        # Delay between applications
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
            print("\n" + "=" * 60)
            print("🎉 JOB APPLICATION PROCESS COMPLETE!")
            print("=" * 60)
            print(f"📊 Applications Sent: {self.applications_sent}")
            print(f"🎯 Target: {self.max_applications}")
            if self.max_applications > 0:
                success_rate = (self.applications_sent / self.max_applications) * 100
                print(f"📈 Success Rate: {success_rate:.1f}%")
            print("=" * 60)

        except KeyboardInterrupt:
            print("\n⚠️ Process interrupted")
            print(f"📊 Applications sent: {self.applications_sent}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print(f"📊 Applications sent: {self.applications_sent}")
        finally:
            print("\n👋 Closing browser...")
            self.driver.quit()

if __name__ == '__main__':
    print("🚀 Fixed LinkedIn Job Applier")
    print("🎯 Reliable Easy Apply button clicking")
    print("=" * 60)

    try:
        applier = FixedLinkedInApplier("user_profile.json")
        applier.run()
    except FileNotFoundError:
        print("❌ user_profile.json not found!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
