#!/usr/bin/env python3
"""
🚀 Robust LinkedIn Job Applier
Fixed version that doesn't close browser suddenly and handles all edge cases
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import json
import os
import tkinter as tk
from tkinter import messagebox
import traceback

class RobustLinkedInApplier:
    def __init__(self):
        """Initialize the robust LinkedIn applier"""
        print("🚀 Initializing Robust LinkedIn Job Applier...")
        
        # Load user profile
        try:
            with open('user_profile.json', 'r') as f:
                self.profile = json.load(f)
            print("✅ User profile loaded")
        except:
            print("⚠️ user_profile.json not found, using defaults")
            self.profile = self.get_default_profile()
        
        # Credentials and settings
        self.email = "tivep27728@devdigs.com"
        self.password = "Mani!8897"
        self.keywords = "Python Developer"
        self.location = "Remote"
        self.max_applications = 25
        self.applications_sent = 0
        
        print(f"🔐 Email: {self.email}")
        print(f"🔍 Search: {self.keywords} in {self.location}")
        print(f"🎯 Target: {self.max_applications} applications")
        
        # Setup Chrome driver
        self.driver = None
        self.wait = None
        self.setup_driver()

    def get_default_profile(self):
        """Default profile if file not found"""
        return {
            'personal_info': {
                'first_name': 'John',
                'last_name': 'Developer',
                'full_name': 'John Developer',
                'email': 'tivep27728@devdigs.com',
                'phone': '+1-555-123-4567'
            }
        }

    def setup_driver(self):
        """Setup Chrome driver with robust error handling"""
        try:
            print("🔧 Setting up Chrome driver...")
            
            chrome_options = Options()
            
            # Basic stealth options
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Window settings
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            
            # Disable notifications and popups
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            
            # Keep browser open on errors
            chrome_options.add_experimental_option("detach", True)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute stealth scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 20)  # Increased timeout
            
            print("✅ Chrome driver setup complete")
            
        except Exception as e:
            print(f"❌ Driver setup failed: {e}")
            print("📋 Full error:")
            traceback.print_exc()
            raise

    def human_delay(self, min_sec=2, max_sec=5):
        """Human-like delays with progress indication"""
        delay = random.uniform(min_sec, max_sec)
        print(f"⏳ Waiting {delay:.1f} seconds...")
        time.sleep(delay)

    def type_like_human(self, element, text):
        """Type with human-like speed and error handling"""
        try:
            element.clear()
            time.sleep(0.5)
            
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            print(f"✅ Typed: {text}")
            return True
        except Exception as e:
            print(f"❌ Typing failed: {e}")
            return False

    def show_popup(self, title, message):
        """Show popup for manual intervention"""
        print(f"\n🚨 {title}")
        print(f"📋 {message}")
        print("=" * 60)
        
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            root.lift()
            root.focus_force()
            
            messagebox.showinfo(f"🚨 {title}", message)
            root.destroy()
            print("✅ User acknowledged popup")
            return True
        except Exception as e:
            print(f"⚠️ Popup failed: {e}")
            print("⌨️ Press ENTER to continue...")
            try:
                input()
                return True
            except:
                return False

    def check_for_manual_intervention(self):
        """Check if manual intervention is needed"""
        try:
            current_url = self.driver.current_url.lower()
            page_source = self.driver.page_source.lower()
            
            # Check for various intervention scenarios
            interventions = [
                ('captcha', 'CAPTCHA detected'),
                ('recaptcha', 'reCAPTCHA detected'),
                ('verify you are human', 'Human verification required'),
                ('security check', 'Security check required'),
                ('challenge', 'Security challenge detected'),
                ('two-factor', 'Two-factor authentication required'),
                ('verification code', 'Verification code required'),
                ('blocked', 'Account temporarily blocked'),
                ('restricted', 'Access restricted')
            ]
            
            for indicator, description in interventions:
                if indicator in current_url or indicator in page_source:
                    print(f"🚨 {description}")
                    return self.show_popup(
                        "Manual Action Required",
                        f"{description}\n\nPlease complete the required action in the browser window, then click OK to continue the automation."
                    )
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error checking for intervention: {e}")
            return False

    def safe_find_element(self, by, value, timeout=10):
        """Safely find element with timeout and error handling"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"⚠️ Element not found: {value}")
            return None
        except Exception as e:
            print(f"⚠️ Error finding element: {e}")
            return None

    def safe_click(self, element, description="element"):
        """Safely click element with multiple methods"""
        if not element:
            print(f"❌ Cannot click {description} - element is None")
            return False
        
        try:
            # Method 1: Regular click
            try:
                element.click()
                print(f"✅ Clicked {description} (regular click)")
                return True
            except ElementClickInterceptedException:
                print(f"⚠️ Click intercepted for {description}, trying JavaScript...")
            
            # Method 2: JavaScript click
            try:
                self.driver.execute_script("arguments[0].click();", element)
                print(f"✅ Clicked {description} (JavaScript click)")
                return True
            except Exception as e:
                print(f"⚠️ JavaScript click failed: {e}")
            
            # Method 3: ActionChains
            try:
                ActionChains(self.driver).move_to_element(element).click().perform()
                print(f"✅ Clicked {description} (ActionChains)")
                return True
            except Exception as e:
                print(f"⚠️ ActionChains click failed: {e}")
            
            print(f"❌ All click methods failed for {description}")
            return False
            
        except Exception as e:
            print(f"❌ Error clicking {description}: {e}")
            return False

    def login_linkedin(self):
        """Robust LinkedIn login with comprehensive error handling"""
        print("\n🔐 Starting LinkedIn login process...")
        
        try:
            # Navigate to login page
            print("🌐 Navigating to LinkedIn login page...")
            self.driver.get("https://www.linkedin.com/login")
            self.human_delay(3, 5)
            
            # Check for manual intervention after page load
            if self.check_for_manual_intervention():
                self.human_delay(2, 3)
            
            # Find and fill email field
            print("📧 Looking for email field...")
            email_field = self.safe_find_element(By.NAME, 'session_key', timeout=15)
            
            if not email_field:
                print("❌ Email field not found")
                return False
            
            if not self.type_like_human(email_field, self.email):
                print("❌ Failed to enter email")
                return False
            
            self.human_delay(1, 2)
            
            # Find and fill password field
            print("🔒 Looking for password field...")
            password_field = self.safe_find_element(By.NAME, 'session_password', timeout=10)
            
            if not password_field:
                print("❌ Password field not found")
                return False
            
            if not self.type_like_human(password_field, self.password):
                print("❌ Failed to enter password")
                return False
            
            self.human_delay(1, 2)
            
            # Submit login
            print("🚀 Submitting login...")
            password_field.send_keys(Keys.RETURN)
            self.human_delay(5, 8)
            
            # Check for manual intervention after login attempt
            max_login_checks = 10
            for attempt in range(max_login_checks):
                print(f"🔍 Login verification attempt {attempt + 1}/{max_login_checks}")
                
                current_url = self.driver.current_url.lower()
                print(f"📍 Current URL: {current_url}")
                
                # Check if login was successful
                if any(indicator in current_url for indicator in ["feed", "/in/", "jobs"]):
                    print("✅ Login successful!")
                    return True
                
                # Check for manual intervention
                if self.check_for_manual_intervention():
                    print("🔄 Manual intervention completed, continuing...")
                    self.human_delay(3, 5)
                    continue
                
                # Check if still on login page
                if "login" in current_url:
                    if attempt < max_login_checks - 1:
                        print("⚠️ Still on login page, waiting...")
                        self.human_delay(3, 5)
                        continue
                    else:
                        print("❌ Login failed - still on login page after all attempts")
                        return False
                
                # Wait and check again
                self.human_delay(3, 5)
            
            print("❌ Login verification timed out")
            return False
            
        except Exception as e:
            print(f"❌ Login error: {e}")
            print("📋 Full error:")
            traceback.print_exc()
            return False

    def search_jobs(self):
        """Search for jobs with robust error handling"""
        print("\n🔍 Starting job search...")
        
        try:
            # Direct URL with Easy Apply filter
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={self.keywords.replace(' ', '%20')}&location={self.location.replace(' ', '%20')}&f_LF=f_AL"
            print(f"🔗 Navigating to: {search_url}")
            
            self.driver.get(search_url)
            self.human_delay(5, 8)
            
            # Check for manual intervention
            if self.check_for_manual_intervention():
                self.human_delay(2, 3)
            
            # Verify we're on jobs page
            current_url = self.driver.current_url.lower()
            if "jobs" not in current_url:
                print("❌ Not on jobs page")
                return False
            
            # Look for job results
            print("🔍 Looking for job results...")
            job_selectors = [
                ".jobs-search-results__list-item",
                ".job-card-container",
                "[data-job-id]"
            ]
            
            job_elements = []
            for selector in job_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        job_elements = elements
                        print(f"✅ Found {len(elements)} jobs using selector: {selector}")
                        break
                except Exception as e:
                    print(f"⚠️ Selector {selector} failed: {e}")
                    continue
            
            if job_elements:
                print(f"✅ Job search successful! Found {len(job_elements)} jobs")
                return True
            else:
                print("❌ No job results found")
                return False
                
        except Exception as e:
            print(f"❌ Job search error: {e}")
            print("📋 Full error:")
            traceback.print_exc()
            return False

    def run_with_error_handling(self):
        """Main execution with comprehensive error handling"""
        print("🚀 Robust LinkedIn Job Applier Starting...")
        print("=" * 60)

        try:
            # Step 1: Login (with retries)
            login_success = False
            for login_attempt in range(3):
                print(f"\n🔐 Login attempt {login_attempt + 1}/3...")

                try:
                    if self.login_linkedin():
                        login_success = True
                        break
                    else:
                        print(f"❌ Login attempt {login_attempt + 1} failed")
                        if login_attempt < 2:
                            print("🔄 Retrying login...")
                            self.human_delay(5, 10)

                except Exception as e:
                    print(f"❌ Login attempt {login_attempt + 1} error: {e}")
                    if login_attempt < 2:
                        print("🔄 Retrying login...")
                        self.human_delay(5, 10)

            if not login_success:
                print("❌ All login attempts failed")
                self.show_popup("Login Failed", "Unable to login to LinkedIn. Please check credentials and try again.")
                return

            # Step 2: Search jobs (with retries)
            search_success = False
            for search_attempt in range(2):
                print(f"\n🔍 Job search attempt {search_attempt + 1}/2...")

                try:
                    if self.search_jobs():
                        search_success = True
                        break
                    else:
                        print(f"❌ Search attempt {search_attempt + 1} failed")
                        if search_attempt < 1:
                            print("🔄 Retrying search...")
                            self.human_delay(3, 5)

                except Exception as e:
                    print(f"❌ Search attempt {search_attempt + 1} error: {e}")
                    if search_attempt < 1:
                        print("🔄 Retrying search...")
                        self.human_delay(3, 5)

            if not search_success:
                print("❌ Job search failed")
                self.show_popup("Search Failed", "Unable to search for jobs. The browser will remain open for manual inspection.")
                return

            # Step 3: Apply to jobs
            print(f"\n🚀 Starting job applications...")
            print(f"🎯 Target: {self.max_applications} applications")
            print("=" * 60)

            page = 1
            consecutive_failures = 0
            max_consecutive_failures = 5

            while self.applications_sent < self.max_applications:
                print(f"\n📄 Processing page {page}...")

                try:
                    # Get job listings
                    job_listings = self.get_job_listings()

                    if not job_listings:
                        print("❌ No job listings found on this page")
                        consecutive_failures += 1

                        if consecutive_failures >= max_consecutive_failures:
                            print("❌ Too many consecutive failures, stopping...")
                            break

                        # Try to go to next page
                        if self.go_to_next_page():
                            page += 1
                            continue
                        else:
                            print("📄 No more pages available")
                            break

                    consecutive_failures = 0  # Reset failure counter
                    print(f"✅ Found {len(job_listings)} jobs on page {page}")

                    # Apply to each job
                    for i, job in enumerate(job_listings):
                        if self.applications_sent >= self.max_applications:
                            print(f"🎯 Reached target of {self.max_applications} applications!")
                            break

                        print(f"\n📋 Job {i+1}/{len(job_listings)} on page {page}")

                        try:
                            success = self.apply_to_job(job)

                            if success:
                                print(f"✅ Application successful! Total: {self.applications_sent}/{self.max_applications}")
                            else:
                                print("❌ Application failed or skipped")

                            # Human delay between applications
                            self.human_delay(5, 10)

                        except Exception as e:
                            print(f"❌ Error processing job: {e}")
                            print("📋 Full error:")
                            traceback.print_exc()
                            continue

                    # Try to go to next page if we haven't reached our target
                    if self.applications_sent < self.max_applications:
                        if self.go_to_next_page():
                            page += 1
                        else:
                            print("📄 No more pages available")
                            break
                    else:
                        break

                except Exception as e:
                    print(f"❌ Error processing page {page}: {e}")
                    print("📋 Full error:")
                    traceback.print_exc()

                    consecutive_failures += 1
                    if consecutive_failures >= max_consecutive_failures:
                        print("❌ Too many page processing failures, stopping...")
                        break

                    # Try to continue to next page
                    if self.go_to_next_page():
                        page += 1
                    else:
                        break

            # Final summary
            self.print_final_summary()

        except KeyboardInterrupt:
            print("\n⚠️ Process interrupted by user")
            print(f"📊 Applications sent before interruption: {self.applications_sent}")
            self.show_popup("Process Interrupted", f"Automation was interrupted. {self.applications_sent} applications were sent.")

        except Exception as e:
            print(f"❌ Unexpected error in main execution: {e}")
            print("📋 Full error:")
            traceback.print_exc()
            self.show_popup("Unexpected Error", f"An unexpected error occurred. {self.applications_sent} applications were sent. The browser will remain open.")

        finally:
            print("\n🔄 Keeping browser open for inspection...")
            self.show_popup("Automation Complete", f"LinkedIn automation finished. {self.applications_sent} applications were sent. You can now inspect the browser or close it manually.")

    def get_job_listings(self):
        """Get job listings with error handling"""
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
                        return elements
                except Exception as e:
                    print(f"⚠️ Selector {selector} failed: {e}")
                    continue

            return []

        except Exception as e:
            print(f"❌ Error getting job listings: {e}")
            return []

    def apply_to_job(self, job_element):
        """Apply to a single job with error handling"""
        try:
            print("📋 Starting job application...")

            # Click job listing
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", job_element)
            self.human_delay(1, 2)

            if not self.safe_click(job_element, "job listing"):
                return False

            self.human_delay(3, 5)

            # Check for manual intervention
            if self.check_for_manual_intervention():
                self.human_delay(2, 3)

            # Get job info
            try:
                title = self.safe_find_element(By.CSS_SELECTOR, "h1", timeout=5)
                title_text = title.text if title else "Unknown Position"
                print(f"📝 Job: {title_text}")
            except:
                title_text = "Unknown Position"

            # Find Easy Apply button
            easy_apply_button = self.find_easy_apply_button()
            if not easy_apply_button:
                print("❌ No Easy Apply button found")
                return False

            # Click Easy Apply
            if not self.safe_click(easy_apply_button, "Easy Apply button"):
                return False

            self.human_delay(3, 5)

            # Complete application
            return self.complete_simple_application(title_text)

        except Exception as e:
            print(f"❌ Job application error: {e}")
            return False

    def find_easy_apply_button(self):
        """Find Easy Apply button"""
        try:
            selectors = [
                "//button[contains(@aria-label, 'Easy Apply')]",
                "//button[contains(text(), 'Easy Apply')]",
                ".jobs-apply-button"
            ]

            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            text = element.text.lower()
                            aria_label = element.get_attribute('aria-label') or ""
                            if 'easy apply' in text or 'easy apply' in aria_label.lower():
                                return element
                except:
                    continue

            return None
        except:
            return None

    def complete_simple_application(self, job_title):
        """Complete application with simple approach"""
        try:
            print("📝 Completing application...")

            # Wait for form to load
            self.human_delay(2, 3)

            # Fill basic fields
            self.fill_basic_fields()

            # Look for submit button
            submit_selectors = [
                "//button[contains(text(), 'Submit application')]",
                "//button[contains(text(), 'Submit')]"
            ]

            for selector in submit_selectors:
                try:
                    submit_btn = self.safe_find_element(By.XPATH, selector, timeout=5)
                    if submit_btn and submit_btn.is_displayed():
                        if self.safe_click(submit_btn, "submit button"):
                            print("✅ Application submitted!")
                            self.applications_sent += 1
                            return True
                except:
                    continue

            # Look for Next button
            next_selectors = [
                "//button[contains(text(), 'Next')]",
                "//button[contains(text(), 'Continue')]"
            ]

            for selector in next_selectors:
                try:
                    next_btn = self.safe_find_element(By.XPATH, selector, timeout=5)
                    if next_btn and next_btn.is_displayed():
                        if self.safe_click(next_btn, "next button"):
                            # Recursively try to complete
                            return self.complete_simple_application(job_title)
                except:
                    continue

            # Complex application
            print("⚠️ Complex application detected")
            if self.show_popup("Manual Application", f"Please complete the application for {job_title} manually and click OK when done."):
                self.applications_sent += 1
                return True

            return False

        except Exception as e:
            print(f"❌ Application completion error: {e}")
            return False

    def fill_basic_fields(self):
        """Fill basic form fields"""
        try:
            inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email'], textarea")

            for field in inputs:
                try:
                    if not field.is_displayed():
                        continue

                    name = field.get_attribute('name') or ""
                    placeholder = field.get_attribute('placeholder') or ""
                    field_info = f"{name} {placeholder}".lower()

                    if 'first' in field_info:
                        self.type_like_human(field, self.profile['personal_info']['first_name'])
                    elif 'last' in field_info:
                        self.type_like_human(field, self.profile['personal_info']['last_name'])
                    elif 'email' in field_info:
                        self.type_like_human(field, self.profile['personal_info']['email'])
                    elif 'phone' in field_info:
                        self.type_like_human(field, self.profile['personal_info']['phone'])

                except:
                    continue

        except Exception as e:
            print(f"⚠️ Form filling error: {e}")

    def go_to_next_page(self):
        """Go to next page of results"""
        try:
            next_button = self.safe_find_element(By.XPATH, "//button[@aria-label='View next page']", timeout=5)
            if next_button and next_button.is_enabled():
                if self.safe_click(next_button, "next page button"):
                    print("📄 Moving to next page...")
                    self.human_delay(5, 8)
                    return True

            return False
        except:
            return False

    def print_final_summary(self):
        """Print final summary"""
        print("\n" + "=" * 60)
        print("🎉 LINKEDIN JOB APPLICATION COMPLETE!")
        print("=" * 60)
        print(f"📊 Applications Sent: {self.applications_sent}")
        print(f"🎯 Target: {self.max_applications}")
        if self.max_applications > 0:
            success_rate = (self.applications_sent / self.max_applications) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")

        if self.applications_sent > 0:
            print("\n✅ NEXT STEPS:")
            print("1. Check your email for application confirmations")
            print("2. Monitor LinkedIn messages for responses")
            print("3. Prepare for potential interviews")

        print("=" * 60)

if __name__ == '__main__':
    print("🚀 Robust LinkedIn Job Applier")
    print("🛡️ Enhanced error handling and browser stability")
    print("=" * 60)

    try:
        applier = RobustLinkedInApplier()
        applier.run_with_error_handling()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("📋 Full error:")
        traceback.print_exc()

        # Keep browser open even on fatal error
        try:
            input("\n⌨️ Press ENTER to close...")
        except:
            pass
