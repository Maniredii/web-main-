#!/usr/bin/env python3
"""
🚀 Working LinkedIn Job Applier
Fixed version that actually clicks Easy Apply buttons and applies to jobs
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import json
import os
import tkinter as tk
from tkinter import messagebox

class WorkingLinkedInApplier:
    def __init__(self):
        """Initialize the LinkedIn applier"""
        # Load user profile
        try:
            with open('user_profile.json', 'r') as f:
                self.profile = json.load(f)
            print("✅ User profile loaded")
        except:
            print("❌ user_profile.json not found, using defaults")
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
        
        # Setup Chrome with stealth
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
        """Setup Chrome driver with stealth options"""
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 15)

    def human_delay(self, min_sec=2, max_sec=5):
        """Human-like delays"""
        time.sleep(random.uniform(min_sec, max_sec))

    def type_like_human(self, element, text):
        """Type with human-like speed"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    def show_popup(self, title, message):
        """Show popup for manual intervention"""
        print(f"\n🚨 {title}")
        print(f"📋 {message}")
        
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            messagebox.showinfo(f"🚨 {title}", message)
            root.destroy()
            return True
        except:
            input("⌨️ Press ENTER to continue...")
            return True

    def login_linkedin(self):
        """Login to LinkedIn"""
        print("🔐 Logging into LinkedIn...")
        
        try:
            self.driver.get("https://www.linkedin.com/login")
            self.human_delay(3, 5)

            # Enter credentials
            email_field = self.wait.until(EC.presence_of_element_located((By.NAME, 'session_key')))
            self.type_like_human(email_field, self.email)
            self.human_delay(1, 2)

            password_field = self.driver.find_element(By.NAME, 'session_password')
            self.type_like_human(password_field, self.password)
            self.human_delay(1, 2)

            # Submit
            password_field.send_keys(Keys.RETURN)
            self.human_delay(5, 8)
            
            # Check success
            current_url = self.driver.current_url.lower()
            if any(x in current_url for x in ["feed", "/in/", "jobs"]):
                print("✅ Login successful!")
                return True
            else:
                print("❌ Login may have failed")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def search_jobs(self):
        """Search for jobs"""
        print("🔍 Searching for jobs...")
        
        try:
            # Direct URL with Easy Apply filter
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={self.keywords.replace(' ', '%20')}&location={self.location.replace(' ', '%20')}&f_LF=f_AL"
            print(f"🔗 URL: {search_url}")
            
            self.driver.get(search_url)
            self.human_delay(5, 8)
            
            # Verify results
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".jobs-search-results__list-item, .job-card-container")
            if job_cards:
                print(f"✅ Found {len(job_cards)} jobs!")
                return True
            else:
                print("❌ No jobs found")
                return False
                
        except Exception as e:
            print(f"❌ Search error: {e}")
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
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return elements
            
            return []
        except:
            return []

    def click_easy_apply_reliably(self):
        """Reliably click Easy Apply button"""
        print("🎯 Looking for Easy Apply button...")
        
        # Wait for page to load
        self.human_delay(2, 3)
        
        # Multiple selector strategies
        selectors = [
            "//button[contains(@aria-label, 'Easy Apply to')]",
            "//button[contains(@aria-label, 'Easy Apply')]",
            "//button[contains(text(), 'Easy Apply')]",
            "//span[contains(text(), 'Easy Apply')]/parent::button",
            ".jobs-apply-button"
        ]
        
        for i, selector in enumerate(selectors, 1):
            try:
                print(f"🔍 Trying method {i}...")
                
                if selector.startswith("//"):
                    buttons = self.driver.find_elements(By.XPATH, selector)
                else:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for button in buttons:
                    if button.is_displayed() and button.is_enabled():
                        text = button.text.lower()
                        aria_label = button.get_attribute('aria-label') or ""
                        
                        if 'easy apply' in text or 'easy apply' in aria_label.lower():
                            print(f"✅ Found Easy Apply button!")
                            
                            # Try multiple click methods
                            for click_method in ['click', 'js_click', 'action_click']:
                                try:
                                    if click_method == 'click':
                                        button.click()
                                    elif click_method == 'js_click':
                                        self.driver.execute_script("arguments[0].click();", button)
                                    elif click_method == 'action_click':
                                        ActionChains(self.driver).move_to_element(button).click().perform()
                                    
                                    print(f"✅ Clicked Easy Apply using {click_method}!")
                                    self.human_delay(3, 5)
                                    
                                    # Check if application modal opened
                                    if self.check_application_opened():
                                        return True
                                    
                                except Exception as e:
                                    print(f"⚠️ {click_method} failed: {e}")
                                    continue
                            
            except Exception as e:
                print(f"⚠️ Method {i} failed: {e}")
                continue
        
        print("❌ Could not click Easy Apply button")
        return False

    def check_application_opened(self):
        """Check if application form opened"""
        try:
            # Look for application modal indicators
            indicators = [
                ".jobs-easy-apply-modal",
                ".artdeco-modal",
                "//h3[contains(text(), 'Submit application')]",
                "//button[contains(text(), 'Submit application')]"
            ]
            
            for indicator in indicators:
                try:
                    if indicator.startswith("//"):
                        element = self.driver.find_element(By.XPATH, indicator)
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    
                    if element.is_displayed():
                        print("✅ Application form opened!")
                        return True
                except:
                    continue
            
            return False
        except:
            return False

    def complete_application(self):
        """Complete the application form"""
        try:
            print("📝 Completing application...")
            
            # Fill basic fields
            self.fill_basic_fields()
            
            # Look for submit button
            submit_selectors = [
                "//button[contains(text(), 'Submit application')]",
                "//button[contains(text(), 'Submit')]",
                "//button[contains(@aria-label, 'Submit application')]"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_btn = self.driver.find_element(By.XPATH, selector)
                    if submit_btn.is_displayed() and submit_btn.is_enabled():
                        submit_btn.click()
                        print("✅ Application submitted!")
                        self.applications_sent += 1
                        self.human_delay(3, 5)
                        return True
                except:
                    continue
            
            # Look for Next button if no submit
            next_selectors = [
                "//button[contains(text(), 'Next')]",
                "//button[contains(text(), 'Continue')]"
            ]
            
            for selector in next_selectors:
                try:
                    next_btn = self.driver.find_element(By.XPATH, selector)
                    if next_btn.is_displayed() and next_btn.is_enabled():
                        next_btn.click()
                        self.human_delay(2, 3)
                        # Recursively try to complete
                        return self.complete_application()
                except:
                    continue
            
            # Complex application - ask for manual help
            print("⚠️ Complex application detected")
            if self.show_popup("Manual Application Required", 
                              "This application requires manual completion. Please fill it out and submit, then click OK."):
                self.applications_sent += 1
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Application completion error: {e}")
            return False

    def fill_basic_fields(self):
        """Fill basic form fields"""
        try:
            # Find text inputs
            inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email'], textarea")
            
            for input_field in inputs:
                try:
                    if not input_field.is_displayed():
                        continue
                    
                    # Get field info
                    name = input_field.get_attribute('name') or ""
                    placeholder = input_field.get_attribute('placeholder') or ""
                    aria_label = input_field.get_attribute('aria-label') or ""
                    field_info = f"{name} {placeholder} {aria_label}".lower()
                    
                    # Fill based on field type
                    if 'first' in field_info or 'fname' in field_info:
                        input_field.clear()
                        input_field.send_keys(self.profile['personal_info']['first_name'])
                    elif 'last' in field_info or 'lname' in field_info:
                        input_field.clear()
                        input_field.send_keys(self.profile['personal_info']['last_name'])
                    elif 'email' in field_info:
                        input_field.clear()
                        input_field.send_keys(self.profile['personal_info']['email'])
                    elif 'phone' in field_info:
                        input_field.clear()
                        input_field.send_keys(self.profile['personal_info']['phone'])
                    
                    self.human_delay(0.5, 1)
                    
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Form filling error: {e}")

    def apply_to_job(self, job_element):
        """Apply to a single job"""
        try:
            print("\n📋 Applying to job...")
            
            # Click job listing
            self.driver.execute_script("arguments[0].scrollIntoView(true);", job_element)
            self.human_delay(1, 2)
            job_element.click()
            self.human_delay(3, 5)
            
            # Get job info
            try:
                title = self.driver.find_element(By.CSS_SELECTOR, "h1").text
                company = self.driver.find_element(By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__company-name").text
                print(f"📝 Job: {title} at {company}")
            except:
                print("📝 Job: Unknown position")
            
            # Click Easy Apply
            if self.click_easy_apply_reliably():
                # Complete application
                return self.complete_application()
            else:
                print("❌ Could not find or click Easy Apply button")
                return False
                
        except Exception as e:
            print(f"❌ Job application error: {e}")
            return False

    def run(self):
        """Main execution"""
        print("🚀 Working LinkedIn Job Applier Starting...")
        print("=" * 60)

        try:
            self.driver.maximize_window()

            # Step 1: Login
            if not self.login_linkedin():
                print("❌ Login failed, stopping")
                return

            # Step 2: Search jobs
            if not self.search_jobs():
                print("❌ Job search failed, stopping")
                return

            # Step 3: Apply to jobs
            print(f"\n🚀 Starting job applications...")
            print("=" * 60)

            page = 1
            while self.applications_sent < self.max_applications:
                print(f"\n📄 Processing page {page}...")

                # Get job listings
                job_listings = self.get_job_listings()

                if not job_listings:
                    print("❌ No job listings found")
                    break

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
                        continue

                # Try to go to next page
                if self.applications_sent < self.max_applications:
                    try:
                        next_button = self.driver.find_element(By.XPATH, "//button[@aria-label='View next page']")
                        if next_button.is_enabled():
                            next_button.click()
                            print("📄 Moving to next page...")
                            self.human_delay(5, 8)
                            page += 1
                        else:
                            print("📄 No more pages available")
                            break
                    except:
                        print("📄 No more pages available")
                        break
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

            if self.applications_sent > 0:
                print("\n✅ NEXT STEPS:")
                print("1. Check your email for application confirmations")
                print("2. Monitor LinkedIn messages for recruiter responses")
                print("3. Prepare for potential interviews")

            print("=" * 60)

        except KeyboardInterrupt:
            print("\n⚠️ Process interrupted by user")
            print(f"📊 Applications sent: {self.applications_sent}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print(f"📊 Applications sent: {self.applications_sent}")
        finally:
            print("\n👋 Closing browser...")
            try:
                self.driver.quit()
            except:
                pass

if __name__ == '__main__':
    print("🚀 Working LinkedIn Job Applier")
    print("🎯 Fixed Easy Apply button clicking")
    print("=" * 60)

    try:
        applier = WorkingLinkedInApplier()
        applier.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
