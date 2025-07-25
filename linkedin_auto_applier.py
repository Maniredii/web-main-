#!/usr/bin/env python3
"""
🚀 LinkedIn Auto Applier - Simple & Fast
No AI needed, just pure automation
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import json
import random
from datetime import datetime

class LinkedInAutoApplier:
    def __init__(self, data):
        """Initialize with configuration data"""
        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']
        self.applications_count = 0
        self.max_applications = data.get('max_applications', 50)
        
        # Setup Chrome with stealth options
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        # Auto-manage ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 10)

    def human_delay(self, min_seconds=1, max_seconds=3):
        """Add random human-like delays"""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def login_linkedin(self):
        """Login to LinkedIn with stealth techniques"""
        print("🔐 Logging into LinkedIn...")
        
        self.driver.get("https://www.linkedin.com/login")
        self.human_delay(2, 4)

        try:
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

            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            print("✅ Login successful!")
            self.human_delay(3, 5)
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
        
        return True

    def type_like_human(self, element, text):
        """Type text with human-like delays"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    def job_search(self):
        """Search for jobs with keywords and location"""
        print(f"🔍 Searching for '{self.keywords}' jobs in '{self.location}'...")

        try:
            # Go directly to jobs search URL
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={self.keywords.replace(' ', '%20')}&location={self.location.replace(' ', '%20')}"
            self.driver.get(search_url)
            self.human_delay(3, 5)

            print("✅ Search completed!")

        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False

        return True

    def apply_easy_apply_filter(self):
        """Apply Easy Apply filter using URL parameter"""
        print("🔧 Applying Easy Apply filter...")

        try:
            # Add Easy Apply filter to current URL
            current_url = self.driver.current_url
            if "f_LF=f_AL" not in current_url:
                if "?" in current_url:
                    filtered_url = current_url + "&f_LF=f_AL"
                else:
                    filtered_url = current_url + "?f_LF=f_AL"

                self.driver.get(filtered_url)
                self.human_delay(3, 5)

            print("✅ Easy Apply filter applied!")

        except Exception as e:
            print(f"❌ Filter failed: {e}")
            return False

        return True

    def get_job_listings(self):
        """Get all job listings on current page"""
        try:
            # Updated selectors for 2024 LinkedIn interface
            selectors = [
                ".jobs-search-results__list-item",
                ".job-card-container",
                "[data-job-id]",
                ".scaffold-layout__list-item",
                ".jobs-search-results-list__item",
                "[data-occludable-job-id]"
            ]

            job_listings = []
            for selector in selectors:
                job_listings = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if job_listings:
                    print(f"✅ Found {len(job_listings)} jobs using selector: {selector}")
                    break

            if not job_listings:
                print("❌ No job listings found with any selector")
                print("🔍 Checking page source for job elements...")

                # Check if we're on the right page
                current_url = self.driver.current_url
                page_title = self.driver.title
                print(f"📍 Current URL: {current_url}")
                print(f"📄 Page Title: {page_title}")

                # Look for any job-related elements
                job_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='job']")
                print(f"🔍 Found {len(job_elements)} elements with 'job' in class name")

                # Take screenshot for debugging
                self.driver.save_screenshot("no_jobs_found.png")
                print("📸 Screenshot saved as 'no_jobs_found.png' for debugging")

            return job_listings
        except Exception as e:
            print(f"❌ Error getting job listings: {e}")
            return []

    def apply_to_job(self, job_element):
        """Apply to a single job"""
        try:
            # Scroll to job and click
            self.driver.execute_script("arguments[0].scrollIntoView(true);", job_element)
            self.human_delay(1, 2)
            job_element.click()
            self.human_delay(2, 3)

            # Get job title
            try:
                job_title = self.driver.find_element(By.CSS_SELECTOR, "h1.t-24").text
                print(f"📝 Applying to: {job_title}")
            except:
                job_title = "Unknown Position"

            # Click Easy Apply button
            try:
                # Try multiple selectors for Easy Apply button
                easy_apply_selectors = [
                    "//button[contains(@aria-label, 'Easy Apply')]",
                    "//button[contains(text(), 'Easy Apply')]",
                    "//button[contains(@class, 'easy-apply')]",
                    ".jobs-apply-button--top-card"
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

                if easy_apply_btn:
                    easy_apply_btn.click()
                    print("✅ Easy Apply button clicked!")
                    self.human_delay(2, 3)
                else:
                    print("❌ Easy Apply button not found, skipping...")
                    return False

            except Exception as e:
                print(f"❌ Error clicking Easy Apply: {e}")
                return False

            # Handle application process
            return self.complete_application()

        except Exception as e:
            print(f"❌ Error applying to job: {e}")
            return False

    def complete_application(self):
        """Complete the application process"""
        try:
            # Check if it's a simple one-click application
            submit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Submit application')]")
            
            if submit_buttons:
                # Simple application - just submit
                submit_buttons[0].click()
                print("✅ Application submitted successfully!")
                self.applications_count += 1
                self.human_delay(2, 3)
                return True
            else:
                # Complex application with forms - skip for now
                print("⚠️ Complex application detected, skipping...")
                self.close_application_modal()
                return False

        except Exception as e:
            print(f"❌ Error completing application: {e}")
            self.close_application_modal()
            return False

    def close_application_modal(self):
        """Close application modal if open"""
        try:
            close_buttons = self.driver.find_elements(By.XPATH, "//button[@aria-label='Dismiss']")
            if close_buttons:
                close_buttons[0].click()
                self.human_delay(1, 2)
                
                # Confirm discard if prompted
                discard_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Discard')]")
                if discard_buttons:
                    discard_buttons[0].click()
                    self.human_delay(1, 2)
        except:
            pass

    def process_all_jobs(self):
        """Process all jobs across multiple pages"""
        print("🚀 Starting job application process...")
        
        page_number = 1
        
        while self.applications_count < self.max_applications:
            print(f"\n📄 Processing page {page_number}...")
            
            # Get job listings on current page
            job_listings = self.get_job_listings()
            
            if not job_listings:
                print("❌ No job listings found, ending...")
                break
            
            print(f"Found {len(job_listings)} jobs on this page")
            
            # Apply to each job
            for i, job in enumerate(job_listings):
                if self.applications_count >= self.max_applications:
                    print(f"🎯 Reached maximum applications ({self.max_applications})")
                    break
                
                print(f"\n📋 Processing job {i+1}/{len(job_listings)}")
                success = self.apply_to_job(job)
                
                if success:
                    print(f"✅ Total applications sent: {self.applications_count}")
                
                # Human-like delay between applications
                self.human_delay(3, 8)
            
            # Try to go to next page
            if self.applications_count < self.max_applications:
                if not self.go_to_next_page():
                    print("📄 No more pages available")
                    break
                page_number += 1
            
        print(f"\n🎉 Application process completed!")
        print(f"📊 Total applications sent: {self.applications_count}")

    def go_to_next_page(self):
        """Navigate to next page of results"""
        try:
            next_button = self.driver.find_element(By.XPATH, "//button[@aria-label='View next page']")
            if next_button.is_enabled():
                next_button.click()
                self.human_delay(3, 5)
                return True
        except:
            pass
        return False

    def run(self):
        """Main execution method"""
        try:
            print("🤖 LinkedIn Auto Applier Starting...")
            print("=" * 50)
            
            self.driver.maximize_window()
            
            # Login
            if not self.login_linkedin():
                return
            
            # Search for jobs
            if not self.job_search():
                return
            
            # Apply filters
            if not self.apply_easy_apply_filter():
                return
            
            # Process all jobs
            self.process_all_jobs()
            
        except KeyboardInterrupt:
            print("\n⚠️ Process interrupted by user")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            print("\n👋 Closing browser...")
            self.driver.quit()

def create_config():
    """Create configuration file"""
    config = {
        "email": "your.email@example.com",
        "password": "your_password",
        "keywords": "Python Developer",
        "location": "Remote",
        "max_applications": 50
    }
    
    with open('linkedin_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("📝 Created linkedin_config.json - Please update with your details!")

if __name__ == '__main__':
    try:
        with open('linkedin_config.json') as config_file:
            data = json.load(config_file)
        
        bot = LinkedInAutoApplier(data)
        bot.run()
        
    except FileNotFoundError:
        print("❌ Configuration file not found!")
        create_config()
        print("Please update linkedin_config.json and run again.")
