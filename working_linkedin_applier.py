#!/usr/bin/env python3
"""
🚀 Working LinkedIn Auto Applier
Based on your simple Selenium approach - MUCH BETTER than AI complexity!
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import json
import os
from dotenv import load_dotenv

class WorkingLinkedInApplier:
    def __init__(self, config=None):
        """Initialize with configuration"""
        # Load environment variables
        load_dotenv()

        # Use .env credentials if available, otherwise use config
        self.email = "tivep27728@devdigs.com"  # From .env file
        self.password = "Mani!8897"  # From .env file

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
        
        # Setup Chrome with anti-detection
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

    def login_linkedin(self):
        """Login to LinkedIn"""
        print(f"🔐 Logging into LinkedIn with: {self.email}")

        try:
            self.driver.get("https://www.linkedin.com/login")
            self.human_delay(2, 4)

            # Enter email
            email_field = self.wait.until(EC.presence_of_element_located((By.NAME, 'session_key')))
            email_field.clear()
            print(f"📧 Entering email: {self.email}")
            self.type_like_human(email_field, self.email)
            self.human_delay(1, 2)

            # Enter password
            password_field = self.driver.find_element(By.NAME, 'session_password')
            password_field.clear()
            print("🔑 Entering password...")
            self.type_like_human(password_field, self.password)
            self.human_delay(1, 2)

            # Click login
            print("🚀 Clicking login button...")
            password_field.send_keys(Keys.RETURN)

            # Wait and check if login was successful
            self.human_delay(5, 8)

            # Check if we're redirected to feed or if there's an error
            current_url = self.driver.current_url
            print(f"📍 Current URL after login: {current_url}")

            if "feed" in current_url or "linkedin.com/in/" in current_url or "linkedin.com/jobs" in current_url:
                print("✅ Login successful!")
                return True
            elif "challenge" in current_url:
                print("⚠️ LinkedIn security challenge detected!")
                print("🔒 Please complete the challenge manually in the browser")
                input("Press Enter after completing the challenge...")
                return True
            else:
                print("❌ Login may have failed - please check manually")
                # Take screenshot for debugging
                self.driver.save_screenshot("login_result.png")
                print("📸 Screenshot saved as 'login_result.png'")
                return False

        except Exception as e:
            print(f"❌ Login failed: {e}")
            # Take screenshot for debugging
            self.driver.save_screenshot("login_error.png")
            print("📸 Screenshot saved as 'login_error.png'")
            return False

    def search_jobs(self):
        """Search for jobs"""
        print(f"🔍 Searching for '{self.keywords}' in '{self.location}'...")
        
        try:
            # Go to jobs page
            self.driver.get("https://www.linkedin.com/jobs/")
            self.human_delay(2, 3)

            # Search keywords
            keyword_box = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[aria-label*='Search jobs']")
            ))
            keyword_box.clear()
            self.type_like_human(keyword_box, self.keywords)
            self.human_delay(1, 2)

            # Search location
            location_box = self.driver.find_element(By.CSS_SELECTOR, "input[aria-label*='Search location']")
            location_box.clear()
            self.type_like_human(location_box, self.location)
            location_box.send_keys(Keys.RETURN)
            
            print("✅ Search completed!")
            self.human_delay(3, 5)
            return True
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False

    def apply_easy_apply_filter(self):
        """Apply Easy Apply filter"""
        print("🔧 Applying Easy Apply filter...")
        
        try:
            # Look for filter button
            filter_button = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@aria-label, 'Show all filters') or contains(text(), 'All filters')]")
            ))
            filter_button.click()
            self.human_delay(2, 3)

            # Find and click Easy Apply checkbox
            easy_apply_checkbox = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//input[@id='f_LF-f_AL'] | //label[contains(text(), 'Easy Apply')]")
            ))
            if not easy_apply_checkbox.is_selected():
                easy_apply_checkbox.click()
            self.human_delay(1, 2)

            # Apply filter
            apply_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Show results') or contains(@aria-label, 'Apply')]")
            apply_button.click()
            
            print("✅ Easy Apply filter applied!")
            self.human_delay(3, 5)
            return True
            
        except Exception as e:
            print(f"⚠️ Filter failed, continuing anyway: {e}")
            return True  # Continue even if filter fails

    def get_job_cards(self):
        """Get job cards from current page"""
        try:
            # Multiple selectors for job cards
            selectors = [
                ".jobs-search-results__list-item",
                ".job-card-container",
                "[data-job-id]",
                ".scaffold-layout__list-item"
            ]
            
            for selector in selectors:
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if job_cards:
                    print(f"✅ Found {len(job_cards)} jobs using {selector}")
                    return job_cards
            
            print("❌ No job cards found")
            return []
            
        except Exception as e:
            print(f"❌ Error getting job cards: {e}")
            return []

    def apply_to_job(self, job_card):
        """Apply to a single job"""
        try:
            # Click on job card
            self.driver.execute_script("arguments[0].scrollIntoView(true);", job_card)
            self.human_delay(1, 2)
            job_card.click()
            self.human_delay(2, 3)

            # Get job title
            try:
                job_title = self.driver.find_element(By.CSS_SELECTOR, "h1").text
                print(f"📝 Applying to: {job_title}")
            except:
                job_title = "Unknown Position"

            # Look for Easy Apply button
            easy_apply_selectors = [
                "//button[contains(@aria-label, 'Easy Apply')]",
                "//button[contains(text(), 'Easy Apply')]",
                ".jobs-apply-button"
            ]
            
            easy_apply_btn = None
            for selector in easy_apply_selectors:
                try:
                    if selector.startswith("//"):
                        easy_apply_btn = self.driver.find_element(By.XPATH, selector)
                    else:
                        easy_apply_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if easy_apply_btn and easy_apply_btn.is_displayed():
                        break
                except:
                    continue

            if not easy_apply_btn:
                print("❌ No Easy Apply button found, skipping...")
                return False

            # Click Easy Apply
            easy_apply_btn.click()
            self.human_delay(2, 3)

            # Handle application modal
            return self.complete_application()

        except Exception as e:
            print(f"❌ Error applying to job: {e}")
            return False

    def complete_application(self):
        """Complete the application process"""
        try:
            # Look for submit button
            submit_selectors = [
                "//button[contains(@aria-label, 'Submit application')]",
                "//button[contains(text(), 'Submit application')]",
                "//button[contains(text(), 'Submit')]"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_btn = self.driver.find_element(By.XPATH, selector)
                    if submit_btn and submit_btn.is_displayed():
                        submit_btn.click()
                        print("✅ Application submitted!")
                        self.applications_sent += 1
                        self.human_delay(2, 3)
                        return True
                except:
                    continue

            # If no submit button, it's a complex application - skip it
            print("⚠️ Complex application detected, skipping...")
            self.close_modal()
            return False

        except Exception as e:
            print(f"❌ Error completing application: {e}")
            self.close_modal()
            return False

    def close_modal(self):
        """Close any open modals"""
        try:
            close_selectors = [
                "//button[@aria-label='Dismiss']",
                "//button[contains(text(), 'Discard')]",
                ".artdeco-modal__dismiss"
            ]
            
            for selector in close_selectors:
                try:
                    close_btn = self.driver.find_element(By.XPATH, selector)
                    if close_btn and close_btn.is_displayed():
                        close_btn.click()
                        self.human_delay(1, 2)
                        break
                except:
                    continue
        except:
            pass

    def run(self):
        """Main execution method"""
        print("🤖 Working LinkedIn Auto Applier Starting...")
        print("=" * 50)
        
        try:
            self.driver.maximize_window()
            
            # Login
            if not self.login_linkedin():
                return
            
            # Search jobs
            if not self.search_jobs():
                return
            
            # Apply filter
            self.apply_easy_apply_filter()
            
            # Process jobs
            print(f"🚀 Starting to apply to jobs (max: {self.max_applications})...")
            
            page = 1
            while self.applications_sent < self.max_applications:
                print(f"\n📄 Processing page {page}...")
                
                job_cards = self.get_job_cards()
                if not job_cards:
                    print("❌ No more jobs found")
                    break
                
                for i, job_card in enumerate(job_cards):
                    if self.applications_sent >= self.max_applications:
                        break
                    
                    print(f"\n📋 Job {i+1}/{len(job_cards)} on page {page}")
                    success = self.apply_to_job(job_card)
                    
                    if success:
                        print(f"✅ Total applications: {self.applications_sent}")
                    
                    # Human delay between applications
                    self.human_delay(3, 8)
                
                # Try next page
                try:
                    next_btn = self.driver.find_element(By.XPATH, "//button[@aria-label='View next page']")
                    if next_btn.is_enabled():
                        next_btn.click()
                        self.human_delay(3, 5)
                        page += 1
                    else:
                        break
                except:
                    break
            
            print(f"\n🎉 Application process completed!")
            print(f"📊 Total applications sent: {self.applications_sent}")
            
        except KeyboardInterrupt:
            print("\n⚠️ Process interrupted by user")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            print("\n👋 Closing browser...")
            self.driver.quit()

if __name__ == '__main__':
    print("🤖 LinkedIn Auto Applier - Using .env credentials")
    print("=" * 50)

    # Try to load configuration, but work without it
    config = None
    try:
        with open('linkedin_config.json') as f:
            config = json.load(f)
            print("✅ Loaded additional config from linkedin_config.json")
    except FileNotFoundError:
        print("ℹ️ No config file found, using default settings")
    except Exception as e:
        print(f"⚠️ Config file error: {e}, using defaults")

    try:
        applier = WorkingLinkedInApplier(config)
        applier.run()
    except Exception as e:
        print(f"❌ Error: {e}")
