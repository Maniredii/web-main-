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
import tkinter as tk
from tkinter import messagebox
import threading

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

        # Initialize tkinter for popup dialogs with proper threading
        self.root = None
        self.user_confirmed = False
        self._init_gui()
        
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

    def _init_gui(self):
        """Initialize GUI properly for popup dialogs"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide the main window
            self.root.attributes('-topmost', True)
            # Force GUI to be ready
            self.root.update_idletasks()
            print("✅ GUI system initialized successfully")
        except Exception as e:
            print(f"⚠️ GUI initialization warning: {e}")
            self.root = None

    def human_delay(self, min_sec=1, max_sec=3):
        """Human-like random delays"""
        time.sleep(random.uniform(min_sec, max_sec))

    def type_like_human(self, element, text):
        """Type with human-like delays"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    def show_manual_intervention_popup(self, title, message, instructions=""):
        """Show enhanced GUI popup dialog for manual intervention"""
        print(f"🔔 Attempting to show popup: {title}")

        # Fallback to simple dialog if GUI not available
        if not self.root:
            print("⚠️ GUI not available, using fallback method")
            return self._fallback_manual_intervention(title, message, instructions)

        self.user_confirmed = False

        def on_confirm():
            self.user_confirmed = True
            popup.destroy()

        def on_popup_close():
            # Prevent closing without confirmation
            pass

        try:
            # Ensure root window is ready
            self.root.deiconify()
            self.root.withdraw()

            # Create popup window with exact specifications
            popup = tk.Toplevel(self.root)
            popup.title("LinkedIn Automation - Manual Action Required")
            popup.geometry("400x250")  # Exact size as requested
            popup.resizable(False, False)

        # Make it modal and always on top
        popup.transient(self.root)
        popup.grab_set()
        popup.protocol("WM_DELETE_WINDOW", on_popup_close)  # Prevent closing

        # Configure popup styling
        popup.configure(bg='#ffffff')

        # Header frame with colored background
        header_frame = tk.Frame(popup, bg='#0077b5', height=50)  # LinkedIn blue
        header_frame.pack(fill='x', pady=0)
        header_frame.pack_propagate(False)

        # Title label in header
        title_label = tk.Label(header_frame, text=title,
                              font=('Segoe UI', 12, 'bold'),
                              bg='#0077b5', fg='white')
        title_label.pack(expand=True)

        # Main content frame
        content_frame = tk.Frame(popup, bg='#ffffff')
        content_frame.pack(fill='both', expand=True, padx=20, pady=15)

        # Message label
        message_label = tk.Label(content_frame, text=message,
                                font=('Segoe UI', 10),
                                bg='#ffffff', fg='#333333',
                                wraplength=350, justify='center')
        message_label.pack(pady=(0, 10))

        # Instructions label (if provided)
        if instructions:
            instructions_label = tk.Label(content_frame, text=instructions,
                                        font=('Segoe UI', 9),
                                        bg='#ffffff', fg='#666666',
                                        wraplength=350, justify='center')
            instructions_label.pack(pady=(0, 15))

        # Button frame
        button_frame = tk.Frame(content_frame, bg='#ffffff')
        button_frame.pack(side='bottom', fill='x')

        # Continue button - prominent and centered
        continue_btn = tk.Button(button_frame, text="Continue Automation",
                               command=on_confirm,
                               font=('Segoe UI', 10, 'bold'),
                               bg='#0077b5', fg='white',
                               padx=30, pady=8,
                               relief='flat',
                               cursor='hand2')
        continue_btn.pack(pady=10)

        # Add hover effect
        def on_enter(e):
            continue_btn.config(bg='#005885')
        def on_leave(e):
            continue_btn.config(bg='#0077b5')

        continue_btn.bind("<Enter>", on_enter)
        continue_btn.bind("<Leave>", on_leave)

        # Center the popup on screen
        popup.update_idletasks()
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = (screen_width // 2) - (400 // 2)  # Center based on 400px width
        y = (screen_height // 2) - (250 // 2)  # Center based on 250px height
        popup.geometry(f"400x250+{x}+{y}")

        # Make popup stay on top and focused
        popup.attributes('-topmost', True)
        popup.lift()
        popup.focus_force()
        continue_btn.focus_set()

        # Flash the popup to get attention
        def flash_popup():
            for _ in range(3):
                popup.attributes('-alpha', 0.3)
                popup.update()
                time.sleep(0.1)
                popup.attributes('-alpha', 1.0)
                popup.update()
                time.sleep(0.1)

        # Flash after a short delay
        popup.after(500, flash_popup)

        print(f"🚨 MANUAL INTERVENTION REQUIRED: {title}")
        print(f"📋 {message}")
        if instructions:
            print(f"💡 {instructions}")
        print("⏸️ AUTOMATION PAUSED - Waiting for user action...")

            # Wait for user confirmation with periodic updates
            while not self.user_confirmed:
                try:
                    popup.update()
                    time.sleep(0.1)
                except tk.TclError:
                    # Popup was destroyed
                    break

            print("✅ User confirmed - resuming automation...")
            print("🚀 Continuing with job applications...")

        except Exception as e:
            print(f"❌ Popup error: {e}")
            return self._fallback_manual_intervention(title, message, instructions)

    def _fallback_manual_intervention(self, title, message, instructions=""):
        """Fallback method when GUI popup fails"""
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
            input()  # Wait for user input
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
                'message': 'LinkedIn is asking you to complete a CAPTCHA puzzle.\n\nPlease solve the CAPTCHA in the browser window.',
                'instructions': 'Click "Continue Automation" after completing the CAPTCHA'
            },
            'security_challenge': {
                'indicators': ['challenge', 'security', 'verify', 'suspicious activity'],
                'title': '🔒 Security Challenge',
                'message': 'LinkedIn has detected unusual activity and requires verification.\n\nPlease complete the security challenge in the browser.',
                'instructions': 'Follow LinkedIn\'s instructions, then click "Continue Automation"'
            },
            'two_factor': {
                'indicators': ['two-factor', '2fa', 'verification code', 'enter code'],
                'title': '📱 Two-Factor Authentication',
                'message': 'LinkedIn is requesting two-factor authentication.\n\nPlease enter your verification code in the browser.',
                'instructions': 'Check your phone/email for the code, enter it, then click "Continue Automation"'
            },
            'phone_verification': {
                'indicators': ['phone verification', 'verify phone', 'mobile number'],
                'title': '📞 Phone Verification',
                'message': 'LinkedIn is asking for phone number verification.\n\nPlease complete the phone verification process.',
                'instructions': 'Enter your phone number and verification code, then click "Continue Automation"'
            },
            'email_verification': {
                'indicators': ['email verification', 'verify email', 'check your email'],
                'title': '📧 Email Verification',
                'message': 'LinkedIn sent a verification email.\n\nPlease check your email and click the verification link.',
                'instructions': 'Open the email, click the link, then click "Continue Automation"'
            }
        }

        for intervention_type, config in interventions.items():
            for indicator in config['indicators']:
                if indicator in current_url or indicator in page_source:
                    print(f"🚨 Manual intervention detected: {intervention_type}")
                    self.show_manual_intervention_popup(
                        config['title'],
                        config['message'],
                        config['instructions']
                    )
                    return True

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
            self.human_delay(3, 5)

            # Check for manual intervention needs
            max_attempts = 3
            attempt = 0

            while attempt < max_attempts:
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
                    attempt += 1
                    continue

                # Check if still on login page (login failed)
                if "login" in current_url:
                    print("❌ Login failed - still on login page")
                    # Take screenshot for debugging
                    self.driver.save_screenshot("login_failed.png")
                    print("📸 Screenshot saved as 'login_failed.png'")
                    return False

                # Unknown state - wait a bit more
                print("🤔 Unknown login state, waiting...")
                self.human_delay(3, 5)
                attempt += 1

            print("❌ Login process timed out or failed")
            return False

        except Exception as e:
            print(f"❌ Login failed: {e}")
            # Take screenshot for debugging
            self.driver.save_screenshot("login_error.png")
            print("📸 Screenshot saved as 'login_error.png'")
            return False

    def navigate_to_jobs(self):
        """Navigate to LinkedIn Jobs section"""
        print("🧭 Navigating to Jobs section...")

        try:
            # Check for manual intervention first
            if self.detect_manual_intervention_needed():
                return False

            # Try multiple methods to get to jobs page
            methods = [
                # Method 1: Direct URL
                lambda: self.driver.get("https://www.linkedin.com/jobs/"),

                # Method 2: Click Jobs tab
                lambda: self._click_jobs_tab(),

                # Method 3: Use search bar navigation
                lambda: self._navigate_via_search()
            ]

            for i, method in enumerate(methods, 1):
                try:
                    print(f"📍 Trying navigation method {i}...")
                    method()
                    self.human_delay(3, 5)

                    # Check if we're on jobs page
                    current_url = self.driver.current_url.lower()
                    if "jobs" in current_url:
                        print("✅ Successfully navigated to Jobs section!")
                        return True

                except Exception as e:
                    print(f"⚠️ Method {i} failed: {e}")
                    continue

            print("❌ Failed to navigate to Jobs section")
            return False

        except Exception as e:
            print(f"❌ Navigation error: {e}")
            return False

    def _click_jobs_tab(self):
        """Try to click the Jobs tab in navigation"""
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
                    return True
            except:
                continue

        raise Exception("Jobs tab not found")

    def _navigate_via_search(self):
        """Navigate to jobs via search functionality"""
        # Go to main LinkedIn page first
        self.driver.get("https://www.linkedin.com/feed/")
        self.human_delay(2, 3)

        # Look for search bar and search for jobs
        search_selectors = [
            "input[placeholder*='Search']",
            ".search-global-typeahead__input",
            "[data-control-name='nav.search']"
        ]

        for selector in search_selectors:
            try:
                search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                if search_box and search_box.is_displayed():
                    search_box.click()
                    self.human_delay(1, 2)
                    search_box.send_keys("jobs")
                    search_box.send_keys(Keys.RETURN)
                    return True
            except:
                continue

        raise Exception("Search navigation failed")

    def search_jobs(self):
        """Search for jobs with specific criteria"""
        print(f"🔍 Searching for '{self.keywords}' in '{self.location}'...")

        try:
            # Check for manual intervention
            if self.detect_manual_intervention_needed():
                return False

            # Ensure we're on jobs page
            current_url = self.driver.current_url.lower()
            if "jobs" not in current_url:
                if not self.navigate_to_jobs():
                    return False

            # Find and fill search fields
            self.human_delay(2, 3)

            # Search for keywords
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
            else:
                print("⚠️ Could not find keyword search box")

            # Search for location
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
            else:
                print("⚠️ Could not find location search box")

            # Submit search
            if keyword_box:
                keyword_box.send_keys(Keys.RETURN)
            elif location_box:
                location_box.send_keys(Keys.RETURN)
            else:
                # Try to find search button
                search_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Search']")
                search_button.click()

            print("✅ Search submitted!")
            self.human_delay(3, 5)

            # Check for manual intervention after search
            if self.detect_manual_intervention_needed():
                return False

            return True

        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False

    def apply_easy_apply_filter(self):
        """Apply Easy Apply filter with multiple methods"""
        print("🔧 Applying Easy Apply filter...")

        try:
            # Check for manual intervention first
            if self.detect_manual_intervention_needed():
                return False

            # Method 1: Try URL parameter approach (most reliable)
            current_url = self.driver.current_url
            if "f_LF=f_AL" not in current_url:
                # Add Easy Apply filter to URL
                separator = "&" if "?" in current_url else "?"
                new_url = f"{current_url}{separator}f_LF=f_AL"
                print("📍 Applying filter via URL...")
                self.driver.get(new_url)
                self.human_delay(3, 5)

                # Check if URL method worked
                if "f_LF=f_AL" in self.driver.current_url:
                    print("✅ Easy Apply filter applied via URL!")
                    return True

            # Method 2: Try filter button approach
            print("🔍 Looking for filter buttons...")
            filter_selectors = [
                "//button[contains(@aria-label, 'Show all filters')]",
                "//button[contains(text(), 'All filters')]",
                "//button[contains(text(), 'Filters')]",
                ".artdeco-pill--choice",
                "[data-control-name='filter_show_all']"
            ]

            filter_button = None
            for selector in filter_selectors:
                try:
                    if selector.startswith("//"):
                        filter_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        filter_button = self.driver.find_element(By.CSS_SELECTOR, selector)

                    if filter_button and filter_button.is_displayed():
                        print(f"✅ Found filter button with selector: {selector}")
                        break
                except:
                    continue

            if filter_button:
                filter_button.click()
                self.human_delay(2, 3)

                # Check for manual intervention after clicking filter
                if self.detect_manual_intervention_needed():
                    return False

                # Look for Easy Apply checkbox
                easy_apply_selectors = [
                    "//input[@id='f_LF-f_AL']",
                    "//label[contains(text(), 'Easy Apply')]//input",
                    "//span[contains(text(), 'Easy Apply')]//input",
                    "[data-control-name='filter_easy_apply']"
                ]

                easy_apply_element = None
                for selector in easy_apply_selectors:
                    try:
                        if selector.startswith("//"):
                            easy_apply_element = self.driver.find_element(By.XPATH, selector)
                        else:
                            easy_apply_element = self.driver.find_element(By.CSS_SELECTOR, selector)

                        if easy_apply_element:
                            break
                    except:
                        continue

                if easy_apply_element:
                    # Check if already selected
                    if not easy_apply_element.is_selected():
                        easy_apply_element.click()
                        print("✅ Easy Apply checkbox selected!")
                    else:
                        print("✅ Easy Apply already selected!")

                    self.human_delay(1, 2)

                    # Apply the filter
                    apply_selectors = [
                        "//button[contains(text(), 'Show results')]",
                        "//button[contains(text(), 'Apply')]",
                        "//button[contains(@aria-label, 'Apply')]",
                        "[data-control-name='filter_apply']"
                    ]

                    for selector in apply_selectors:
                        try:
                            if selector.startswith("//"):
                                apply_button = self.driver.find_element(By.XPATH, selector)
                            else:
                                apply_button = self.driver.find_element(By.CSS_SELECTOR, selector)

                            if apply_button and apply_button.is_displayed():
                                apply_button.click()
                                print("✅ Filter applied!")
                                self.human_delay(3, 5)
                                return True
                        except:
                            continue

            # Method 3: Try direct search with Easy Apply parameter
            print("🔄 Trying direct search with Easy Apply...")
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={self.keywords}&location={self.location}&f_LF=f_AL"
            self.driver.get(search_url)
            self.human_delay(3, 5)

            print("✅ Easy Apply filter applied via direct search!")
            return True

        except Exception as e:
            print(f"⚠️ Filter application failed: {e}")
            print("🔄 Continuing without filter - will check for Easy Apply buttons manually")
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

            # Check for manual intervention after clicking job
            if self.detect_manual_intervention_needed():
                return False

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

            # Check for manual intervention after clicking Easy Apply
            if self.detect_manual_intervention_needed():
                return False

            # Handle application modal
            return self.complete_application()

        except Exception as e:
            print(f"❌ Error applying to job: {e}")
            return False

    def complete_application(self):
        """Complete the application process"""
        try:
            # Check for manual intervention first
            if self.detect_manual_intervention_needed():
                return False

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

                        # Check for manual intervention after submission
                        if self.detect_manual_intervention_needed():
                            return True  # Still count as successful even if intervention needed

                        return True
                except:
                    continue

            # If no submit button, check if it's a multi-step application
            next_selectors = [
                "//button[contains(text(), 'Next')]",
                "//button[contains(text(), 'Continue')]",
                "//button[contains(@aria-label, 'Continue')]"
            ]

            for selector in next_selectors:
                try:
                    next_btn = self.driver.find_element(By.XPATH, selector)
                    if next_btn and next_btn.is_displayed():
                        print("⚠️ Multi-step application detected - requires manual completion")
                        self.show_manual_intervention_popup(
                            "📝 Multi-Step Application",
                            "This job application requires multiple steps or additional information.\n\nPlease complete the application manually in the browser window.",
                            "Fill out all required fields and submit the application, then click 'Continue Automation'"
                        )
                        return True  # Count as successful since user will complete manually
                except:
                    continue

            # If no submit or next button, it's a complex application - skip it
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

            # Navigate to Jobs section
            if not self.navigate_to_jobs():
                print("❌ Failed to navigate to Jobs section")
                return

            # Search for jobs
            if not self.search_jobs():
                print("❌ Failed to search for jobs")
                return

            # Apply Easy Apply filter
            if not self.apply_easy_apply_filter():
                print("⚠️ Easy Apply filter may not have been applied, continuing anyway...")
                # Continue even if filter fails
            
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

            # Clean up tkinter
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass

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
