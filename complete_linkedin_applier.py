#!/usr/bin/env python3
"""
🚀 Complete LinkedIn Auto Applier
Full job search and application automation with reliable popup system
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

class CompleteLinkedInApplier:
    def __init__(self, config=None):
        """Initialize with configuration"""
        load_dotenv()
        
        # Credentials
        self.email = "tivep27728@devdigs.com"
        self.password = "Mani!8897"
        
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

    def human_delay(self, min_sec=1, max_sec=3):
        """Human-like random delays"""
        time.sleep(random.uniform(min_sec, max_sec))

    def type_like_human(self, element, text):
        """Type with human-like delays"""
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
            print("🔔 Showing popup window...")
            
            # Create new root window
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            root.lift()
            root.focus_force()
            
            # Combine message and instructions
            full_message = f"{message}\n\n{instructions}" if instructions else message
            
            # Show messagebox
            messagebox.showinfo(
                "🚨 LINKEDIN AUTOMATION - MANUAL ACTION REQUIRED 🚨",
                full_message
            )
            
            root.destroy()
            print("✅ User completed manual intervention!")
            return True
            
        except Exception as e:
            print(f"⚠️ Popup failed: {e}")
            
            # Terminal fallback
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
            },
            'two_factor': {
                'indicators': ['two-factor', '2fa', 'verification code', 'enter code'],
                'title': '📱 Two-Factor Authentication',
                'message': 'LinkedIn is requesting two-factor authentication.\n\nPlease enter your verification code.',
                'instructions': 'Check your phone/email for the code, enter it, then click "OK"'
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
        print(f"🔐 Logging into LinkedIn with: {self.email}")
        
        try:
            self.driver.get("https://www.linkedin.com/login")
            self.human_delay(2, 4)

            # Enter email
            email_field = self.wait.until(EC.presence_of_element_located((By.NAME, 'session_key')))
            email_field.clear()
            self.type_like_human(email_field, self.email)
            self.human_delay(1, 2)

            # Enter password
            password_field = self.driver.find_element(By.NAME, 'session_password')
            password_field.clear()
            self.type_like_human(password_field, self.password)
            self.human_delay(1, 2)

            # Submit login
            password_field.send_keys(Keys.RETURN)
            self.human_delay(3, 5)
            
            # Check for manual intervention
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

    def navigate_to_jobs(self):
        """Navigate to LinkedIn Jobs section"""
        print("🧭 Navigating to Jobs section...")
        
        try:
            # Direct URL navigation
            self.driver.get("https://www.linkedin.com/jobs/")
            self.human_delay(3, 5)
            
            current_url = self.driver.current_url.lower()
            if "jobs" in current_url:
                print("✅ Successfully navigated to Jobs section!")
                return True
            
            print("❌ Failed to navigate to Jobs section")
            return False
            
        except Exception as e:
            print(f"❌ Navigation error: {e}")
            return False

    def search_jobs(self):
        """Search for jobs with specific criteria"""
        print(f"🔍 Searching for '{self.keywords}' in '{self.location}'...")
        
        try:
            self.human_delay(2, 3)
            
            # Find keyword search box
            keyword_selectors = [
                "input[aria-label*='Search jobs']",
                "input[placeholder*='Search jobs']",
                ".jobs-search-box__text-input[aria-label*='Search jobs']"
            ]
            
            keyword_box = None
            for selector in keyword_selectors:
                try:
                    keyword_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if keyword_box and keyword_box.is_displayed():
                        break
                except:
                    continue
            
            if keyword_box:
                keyword_box.clear()
                self.type_like_human(keyword_box, self.keywords)
                print(f"✅ Entered keywords: {self.keywords}")
                self.human_delay(1, 2)
            
            # Find location search box
            location_selectors = [
                "input[aria-label*='Search location']",
                "input[placeholder*='Search location']",
                ".jobs-search-box__text-input[aria-label*='location']"
            ]
            
            location_box = None
            for selector in location_selectors:
                try:
                    location_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if location_box and location_box.is_displayed():
                        break
                except:
                    continue
            
            if location_box:
                location_box.clear()
                self.type_like_human(location_box, self.location)
                print(f"✅ Entered location: {self.location}")
                self.human_delay(1, 2)

            # Submit search
            if keyword_box:
                keyword_box.send_keys(Keys.RETURN)
            elif location_box:
                location_box.send_keys(Keys.RETURN)
            
            print("✅ Search submitted!")
            self.human_delay(3, 5)
            return True
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False

    def apply_easy_apply_filter(self):
        """Apply Easy Apply filter"""
        print("🔧 Applying Easy Apply filter...")

        try:
            current_url = self.driver.current_url
            if "f_LF=f_AL" not in current_url:
                separator = "&" if "?" in current_url else "?"
                new_url = f"{current_url}{separator}f_LF=f_AL"
                self.driver.get(new_url)
                self.human_delay(3, 5)
                print("✅ Easy Apply filter applied!")
            else:
                print("✅ Easy Apply filter already applied!")
            return True

        except Exception as e:
            print(f"⚠️ Filter application failed: {e}")
            return True  # Continue anyway

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
                        print(f"✅ Found {len(elements)} jobs using: {selector}")
                        return elements
                except:
                    continue

            print("❌ No job listings found")
            return []

        except Exception as e:
            print(f"❌ Error getting job listings: {e}")
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

            # Get job title
            try:
                job_title_selectors = ["h1", ".job-details-jobs-unified-top-card__job-title"]
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
            easy_apply_selectors = [
                "//button[contains(@aria-label, 'Easy Apply')]",
                "//button[contains(text(), 'Easy Apply')]",
                ".jobs-apply-button"
            ]

            easy_apply_button = None
            for selector in easy_apply_selectors:
                try:
                    if selector.startswith("//"):
                        easy_apply_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        easy_apply_button = self.driver.find_element(By.CSS_SELECTOR, selector)

                    if easy_apply_button and easy_apply_button.is_displayed():
                        break
                except:
                    continue

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
            max_steps = 5
            current_step = 0

            while current_step < max_steps:
                current_step += 1
                print(f"📋 Application step {current_step}...")

                # Check for manual intervention
                if self.detect_manual_intervention_needed():
                    return True

                # Look for submit button
                submit_selectors = [
                    "//button[contains(@aria-label, 'Submit application')]",
                    "//button[contains(text(), 'Submit application')]",
                    "//button[contains(text(), 'Submit')]"
                ]

                submit_button = None
                for selector in submit_selectors:
                    try:
                        submit_button = self.driver.find_element(By.XPATH, selector)
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
                    "//button[contains(@aria-label, 'Continue')]"
                ]

                next_button = None
                for selector in next_selectors:
                    try:
                        next_button = self.driver.find_element(By.XPATH, selector)
                        if next_button and next_button.is_displayed() and next_button.is_enabled():
                            break
                    except:
                        continue

                if next_button:
                    next_button.click()
                    self.human_delay(2, 3)
                    continue

                # Complex application
                print("⚠️ Complex application detected")
                if self.show_manual_intervention_popup(
                    "📝 Complex Application",
                    "This job application requires additional information.\n\nPlease complete the application manually in the browser.",
                    "Fill out all required fields and submit, then click 'OK' to continue"
                ):
                    return True
                else:
                    return False

            print("⚠️ Application process exceeded maximum steps")
            return False

        except Exception as e:
            print(f"❌ Error completing application: {e}")
            return False

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
        """Main execution with complete job application process"""
        print("🚀 Complete LinkedIn Auto Applier Starting...")
        print("=" * 60)

        try:
            self.driver.maximize_window()

            # Login
            if not self.login_linkedin():
                print("❌ Login failed")
                return

            # Navigate to Jobs
            if not self.navigate_to_jobs():
                print("❌ Navigation failed")
                return

            # Search for jobs
            if not self.search_jobs():
                print("❌ Search failed")
                return

            # Apply Easy Apply filter
            self.apply_easy_apply_filter()

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

                # Apply to each job
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

                        # Delay between applications
                        self.human_delay(3, 8)

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
            print("🎉 Job Application Process Complete!")
            print(f"📊 Total applications sent: {self.applications_sent}")
            print(f"🎯 Target was: {self.max_applications}")
            if self.max_applications > 0:
                print(f"📈 Success rate: {(self.applications_sent/self.max_applications)*100:.1f}%")
            print("=" * 60)

        except KeyboardInterrupt:
            print("\n⚠️ Process interrupted by user")
            print(f"📊 Applications sent: {self.applications_sent}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print(f"📊 Applications sent: {self.applications_sent}")
        finally:
            print("\n👋 Closing browser...")
            self.driver.quit()

if __name__ == '__main__':
    print("🚀 Complete LinkedIn Auto Applier")
    print("🎯 Full job search and application automation")
    print("=" * 60)

    config = None
    try:
        with open('linkedin_config.json') as f:
            config = json.load(f)
        print("✅ Config loaded")
    except:
        print("ℹ️ Using defaults")

    try:
        applier = CompleteLinkedInApplier(config)
        applier.run()
    except Exception as e:
        print(f"❌ Error: {e}")
