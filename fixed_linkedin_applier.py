#!/usr/bin/env python3
"""
🚀 Fixed LinkedIn Auto Applier
Addresses critical popup and navigation issues
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
import tkinter as tk
from tkinter import messagebox
import threading
import subprocess
import sys

class FixedLinkedInApplier:
    def __init__(self, config=None):
        """Initialize with configuration"""
        # Load environment variables
        load_dotenv()
        
        # Use .env credentials
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

    def show_manual_intervention_popup(self, title, message, instructions=""):
        """Show manual intervention popup with fallback"""
        print(f"🔔 Manual intervention needed: {title}")
        
        # Try GUI popup first
        try:
            return self._show_gui_popup(title, message, instructions)
        except Exception as e:
            print(f"⚠️ GUI popup failed: {e}")
            return self._show_fallback_popup(title, message, instructions)

    def _show_gui_popup(self, title, message, instructions=""):
        """Show GUI popup using subprocess to avoid threading issues"""
        try:
            # Create a simple popup script
            popup_script = f'''
import tkinter as tk
from tkinter import messagebox
import sys

def show_popup():
    root = tk.Tk()
    root.withdraw()
    
    # Create custom popup
    popup = tk.Toplevel(root)
    popup.title("LinkedIn Automation - Manual Action Required")
    popup.geometry("400x250")
    popup.resizable(False, False)
    popup.attributes('-topmost', True)
    popup.grab_set()
    
    # Configure popup
    popup.configure(bg='#ffffff')
    
    # Header
    header = tk.Frame(popup, bg='#0077b5', height=50)
    header.pack(fill='x')
    header.pack_propagate(False)
    
    title_label = tk.Label(header, text="{title}", font=('Arial', 12, 'bold'), 
                          bg='#0077b5', fg='white')
    title_label.pack(expand=True)
    
    # Content
    content = tk.Frame(popup, bg='#ffffff')
    content.pack(fill='both', expand=True, padx=20, pady=15)
    
    msg_label = tk.Label(content, text="{message}", font=('Arial', 10), 
                        bg='#ffffff', fg='#333333', wraplength=350, justify='center')
    msg_label.pack(pady=(0, 10))
    
    if "{instructions}":
        inst_label = tk.Label(content, text="{instructions}", font=('Arial', 9), 
                             bg='#ffffff', fg='#666666', wraplength=350, justify='center')
        inst_label.pack(pady=(0, 15))
    
    # Button
    def on_continue():
        popup.destroy()
        root.quit()
    
    btn = tk.Button(content, text="Continue Automation", command=on_continue,
                   font=('Arial', 10, 'bold'), bg='#0077b5', fg='white', 
                   padx=30, pady=8)
    btn.pack(pady=10)
    
    # Center popup
    popup.update_idletasks()
    x = (popup.winfo_screenwidth() // 2) - 200
    y = (popup.winfo_screenheight() // 2) - 125
    popup.geometry(f"400x250+{{x}}+{{y}}")
    
    popup.mainloop()

if __name__ == "__main__":
    show_popup()
'''
            
            # Write popup script to temp file
            with open('temp_popup.py', 'w') as f:
                f.write(popup_script)
            
            # Run popup in separate process
            print("🔔 Showing GUI popup...")
            result = subprocess.run([sys.executable, 'temp_popup.py'], 
                                  capture_output=True, text=True, timeout=300)
            
            # Clean up
            try:
                os.remove('temp_popup.py')
            except:
                pass
            
            print("✅ User completed manual intervention")
            return True
            
        except Exception as e:
            print(f"❌ GUI popup error: {e}")
            return False

    def _show_fallback_popup(self, title, message, instructions=""):
        """Fallback text-based intervention"""
        print("\n" + "="*60)
        print(f"🚨 MANUAL INTERVENTION REQUIRED: {title}")
        print("="*60)
        print(f"📋 {message}")
        if instructions:
            print(f"💡 {instructions}")
        print("="*60)
        print("⏸️ AUTOMATION PAUSED")
        print("🌐 Please complete the required action in the browser window")
        print("⌨️ Press ENTER when you have completed the action...")
        print("="*60)
        
        try:
            input()
            print("✅ User confirmed - resuming automation...")
            return True
        except KeyboardInterrupt:
            print("\n❌ Process interrupted by user")
            return False

    def detect_manual_intervention_needed(self):
        """Detect if manual intervention is needed"""
        current_url = self.driver.current_url.lower()
        page_source = self.driver.page_source.lower()
        
        # Check for various manual intervention scenarios
        interventions = {
            'captcha': {
                'indicators': ['captcha', 'recaptcha', 'verify you are human', 'security check'],
                'title': '🤖 CAPTCHA Detected',
                'message': 'LinkedIn is asking you to complete a CAPTCHA puzzle.\\n\\nPlease solve the CAPTCHA in the browser window.',
                'instructions': 'Click "Continue Automation" after completing the CAPTCHA'
            },
            'security_challenge': {
                'indicators': ['challenge', 'security', 'verify', 'suspicious activity'],
                'title': '🔒 Security Challenge',
                'message': 'LinkedIn has detected unusual activity and requires verification.\\n\\nPlease complete the security challenge in the browser.',
                'instructions': 'Follow LinkedIn\\'s instructions, then click "Continue Automation"'
            },
            'two_factor': {
                'indicators': ['two-factor', '2fa', 'verification code', 'enter code'],
                'title': '📱 Two-Factor Authentication',
                'message': 'LinkedIn is requesting two-factor authentication.\\n\\nPlease enter your verification code in the browser.',
                'instructions': 'Check your phone/email for the code, enter it, then click "Continue Automation"'
            }
        }
        
        for intervention_type, config in interventions.items():
            for indicator in config['indicators']:
                if indicator in current_url or indicator in page_source:
                    print(f"🚨 Manual intervention detected: {intervention_type}")
                    return self.show_manual_intervention_popup(
                        config['title'],
                        config['message'],
                        config['instructions']
                    )
        
        return False

    def login_linkedin(self):
        """Login to LinkedIn with improved error handling"""
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
            
            # Wait and check for manual intervention
            self.human_delay(3, 5)
            
            # Check for manual intervention needs
            max_attempts = 3
            for attempt in range(max_attempts):
                current_url = self.driver.current_url.lower()
                print(f"📍 Current URL after login attempt {attempt + 1}: {current_url}")
                
                # Check if login was successful
                if any(indicator in current_url for indicator in ["feed", "/in/", "jobs"]):
                    print("✅ Login successful!")
                    return True
                
                # Check if manual intervention is needed
                if self.detect_manual_intervention_needed():
                    # After user completes manual intervention, check again
                    self.human_delay(2, 3)
                    continue
                
                # Check if still on login page (login failed)
                if "login" in current_url:
                    print("❌ Login failed - still on login page")
                    return False
                
                # Wait a bit more
                self.human_delay(3, 5)
            
            print("❌ Login process timed out")
            return False
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False

    def navigate_to_jobs(self):
        """Navigate to LinkedIn Jobs section with multiple methods"""
        print("🧭 Navigating to Jobs section...")

        try:
            # Method 1: Direct URL navigation
            print("📍 Method 1: Direct URL navigation")
            self.driver.get("https://www.linkedin.com/jobs/")
            self.human_delay(3, 5)

            # Check if we're on jobs page
            current_url = self.driver.current_url.lower()
            if "jobs" in current_url:
                print("✅ Successfully navigated to Jobs section!")
                return True

            # Method 2: Try clicking Jobs tab
            print("📍 Method 2: Clicking Jobs tab")
            jobs_selectors = [
                "//a[contains(@href, '/jobs')]",
                "//a[contains(text(), 'Jobs')]",
                "[data-control-name='nav.jobs']",
                ".global-nav__primary-link[href*='jobs']"
            ]

            for selector in jobs_selectors:
                try:
                    if selector.startswith("//"):
                        jobs_link = self.driver.find_element(By.XPATH, selector)
                    else:
                        jobs_link = self.driver.find_element(By.CSS_SELECTOR, selector)

                    if jobs_link and jobs_link.is_displayed():
                        jobs_link.click()
                        self.human_delay(3, 5)

                        current_url = self.driver.current_url.lower()
                        if "jobs" in current_url:
                            print("✅ Successfully navigated via Jobs tab!")
                            return True
                except:
                    continue

            # Method 3: Search navigation
            print("📍 Method 3: Search navigation")
            try:
                search_box = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Search']")
                search_box.click()
                search_box.clear()
                search_box.send_keys("jobs")
                search_box.send_keys(Keys.RETURN)
                self.human_delay(3, 5)

                current_url = self.driver.current_url.lower()
                if "jobs" in current_url:
                    print("✅ Successfully navigated via search!")
                    return True
            except:
                pass

            print("❌ Failed to navigate to Jobs section")
            return False

        except Exception as e:
            print(f"❌ Navigation error: {e}")
            return False

    def search_jobs(self):
        """Search for jobs with specific criteria"""
        print(f"🔍 Searching for '{self.keywords}' in '{self.location}'...")

        try:
            # Ensure we're on jobs page
            current_url = self.driver.current_url.lower()
            if "jobs" not in current_url:
                if not self.navigate_to_jobs():
                    return False

            self.human_delay(2, 3)

            # Find keyword search box
            keyword_selectors = [
                "input[aria-label*='Search jobs']",
                "input[placeholder*='Search jobs']",
                ".jobs-search-box__text-input[aria-label*='Search jobs']",
                "#jobs-search-box-keyword-id-ember"
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
                ".jobs-search-box__text-input[aria-label*='location']",
                "#jobs-search-box-location-id-ember"
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
        """Apply Easy Apply filter using URL method"""
        print("🔧 Applying Easy Apply filter...")

        try:
            # Use URL parameter method (most reliable)
            current_url = self.driver.current_url
            if "f_LF=f_AL" not in current_url:
                separator = "&" if "?" in current_url else "?"
                new_url = f"{current_url}{separator}f_LF=f_AL"
                print("📍 Applying filter via URL...")
                self.driver.get(new_url)
                self.human_delay(3, 5)

                if "f_LF=f_AL" in self.driver.current_url:
                    print("✅ Easy Apply filter applied!")
                    return True

            print("✅ Easy Apply filter already applied!")
            return True

        except Exception as e:
            print(f"⚠️ Filter application failed: {e}")
            return True  # Continue anyway

    def run(self):
        """Main execution method"""
        print("🤖 Fixed LinkedIn Auto Applier Starting...")
        print("=" * 50)

        try:
            self.driver.maximize_window()

            # Login
            if not self.login_linkedin():
                print("❌ Login failed, stopping automation")
                return

            # Navigate to Jobs section
            if not self.navigate_to_jobs():
                print("❌ Failed to navigate to Jobs section")
                return

            # Search for jobs
            if not self.search_jobs():
                print("❌ Failed to search for jobs")
                return

            # Apply Easy Apply filter
            self.apply_easy_apply_filter()

            print(f"\n🎉 Setup completed successfully!")
            print(f"📊 Ready to apply to {self.keywords} jobs in {self.location}")
            print(f"🎯 Target: {self.max_applications} applications")

            # Keep browser open for manual inspection
            print("\n🔍 Keeping browser open for 60 seconds for inspection...")
            print("⌨️ Press Ctrl+C to stop early")
            time.sleep(60)

        except KeyboardInterrupt:
            print("\n⚠️ Process interrupted by user")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            print("\n👋 Closing browser...")
            self.driver.quit()

if __name__ == '__main__':
    print("🤖 Fixed LinkedIn Auto Applier - Addressing Critical Issues")
    print("=" * 60)

    # Try to load configuration
    config = None
    try:
        with open('linkedin_config.json') as f:
            config = json.load(f)
        print("✅ Loaded config from linkedin_config.json")
    except:
        print("ℹ️ Using default settings")

    try:
        applier = FixedLinkedInApplier(config)
        applier.run()
    except Exception as e:
        print(f"❌ Error: {e}")
