#!/usr/bin/env python3
"""
🚀 Complete LinkedIn Job Applier
Comprehensive automation with user profile integration and proper job search
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
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
from PIL import Image
import io
import base64

class LinkedInJobApplier:
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
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in {profile_path}!")
            raise
        
        # LinkedIn credentials
        self.email = self.profile['personal_info']['email']
        self.password = os.getenv('LINKEDIN_PASSWORD', 'Mani!8897')
        
        # Job search criteria
        search_criteria = self.profile['search_criteria']
        self.keywords = search_criteria['keywords'][0]  # Use first keyword
        self.location = search_criteria['locations'][0]  # Use first location
        self.max_applications = 25
        self.applications_sent = 0
        
        print(f"🔐 Using email: {self.email}")
        print(f"🔍 Search criteria: {self.keywords} in {self.location}")
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
        self.wait = WebDriverWait(self.driver, 15)

        # Load Easy Apply button templates for computer vision
        self.easy_apply_templates = self.load_easy_apply_templates()

    def load_easy_apply_templates(self):
        """Load Easy Apply button template images for computer vision"""
        templates = []
        template_files = [
            "easy apply image1.png",
            "easy apply image2.webp"
        ]

        for template_file in template_files:
            try:
                if os.path.exists(template_file):
                    # Load image using OpenCV
                    if template_file.endswith('.webp'):
                        # Handle WebP format
                        img = cv2.imread(template_file, cv2.IMREAD_COLOR)
                    else:
                        img = cv2.imread(template_file, cv2.IMREAD_COLOR)

                    if img is not None:
                        # Convert to grayscale for template matching
                        gray_template = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        templates.append({
                            'image': gray_template,
                            'name': template_file,
                            'height': gray_template.shape[0],
                            'width': gray_template.shape[1]
                        })
                        print(f"✅ Loaded Easy Apply template: {template_file}")
                    else:
                        print(f"⚠️ Could not load template: {template_file}")
                else:
                    print(f"⚠️ Template file not found: {template_file}")
            except Exception as e:
                print(f"⚠️ Error loading template {template_file}: {e}")

        if templates:
            print(f"✅ Loaded {len(templates)} Easy Apply templates for computer vision")
        else:
            print("⚠️ No Easy Apply templates loaded - using traditional selectors only")

        return templates

    def take_screenshot(self):
        """Take screenshot of current page"""
        try:
            # Take screenshot
            screenshot = self.driver.get_screenshot_as_png()

            # Convert to OpenCV format
            img_array = np.frombuffer(screenshot, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            # Convert to grayscale for template matching
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            return img, gray_img
        except Exception as e:
            print(f"⚠️ Error taking screenshot: {e}")
            return None, None

    def find_easy_apply_buttons_with_cv(self):
        """Find Easy Apply buttons using computer vision"""
        if not self.easy_apply_templates:
            return []

        try:
            # Take screenshot
            color_img, gray_img = self.take_screenshot()
            if gray_img is None:
                return []

            found_buttons = []

            # Try each template
            for template in self.easy_apply_templates:
                try:
                    # Perform template matching
                    result = cv2.matchTemplate(gray_img, template['image'], cv2.TM_CCOEFF_NORMED)

                    # Find matches above threshold
                    threshold = 0.7  # Adjust threshold as needed
                    locations = np.where(result >= threshold)

                    # Process matches
                    for pt in zip(*locations[::-1]):  # Switch x and y coordinates
                        x, y = pt
                        w, h = template['width'], template['height']

                        # Calculate center point
                        center_x = x + w // 2
                        center_y = y + h // 2

                        # Check if this location is already found (avoid duplicates)
                        is_duplicate = False
                        for existing in found_buttons:
                            if abs(existing['x'] - center_x) < 50 and abs(existing['y'] - center_y) < 50:
                                is_duplicate = True
                                break

                        if not is_duplicate:
                            found_buttons.append({
                                'x': center_x,
                                'y': center_y,
                                'width': w,
                                'height': h,
                                'template': template['name'],
                                'confidence': result[y, x]
                            })
                            print(f"✅ Found Easy Apply button using {template['name']} at ({center_x}, {center_y}) with confidence {result[y, x]:.2f}")

                except Exception as e:
                    print(f"⚠️ Error matching template {template['name']}: {e}")
                    continue

            # Sort by confidence (highest first)
            found_buttons.sort(key=lambda x: x['confidence'], reverse=True)

            return found_buttons

        except Exception as e:
            print(f"⚠️ Error in computer vision detection: {e}")
            return []

    def click_easy_apply_button_cv(self, button_info):
        """Click Easy Apply button using computer vision coordinates"""
        try:
            # Use Selenium's ActionChains to click at specific coordinates
            from selenium.webdriver.common.action_chains import ActionChains

            # Get the body element to calculate relative coordinates
            body = self.driver.find_element(By.TAG_NAME, 'body')

            # Create action chain and click at the button location
            actions = ActionChains(self.driver)
            actions.move_to_element_with_offset(body, button_info['x'], button_info['y'])
            actions.click()
            actions.perform()

            print(f"✅ Clicked Easy Apply button at ({button_info['x']}, {button_info['y']}) using computer vision")
            return True

        except Exception as e:
            print(f"⚠️ Error clicking button with computer vision: {e}")
            return False

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
            print("🔔 Showing popup window...")
            
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
        print(f"🔐 Logging into LinkedIn...")
        
        try:
            self.driver.get("https://www.linkedin.com/login")
            self.human_delay(2, 4)

            # Enter email
            email_field = self.wait.until(EC.presence_of_element_located((By.NAME, 'session_key')))
            self.type_like_human(email_field, self.email)
            print(f"✅ Email entered: {self.email}")
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
                    print("❌ Login failed - still on login page")
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
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={self.keywords.replace(' ', '%20')}&location={self.location.replace(' ', '%20')}"
            print(f"🔍 Searching with URL: {search_url}")
            
            self.driver.get(search_url)
            self.human_delay(5, 8)
            
            # Verify we're on the jobs page
            current_url = self.driver.current_url.lower()
            if "jobs" not in current_url:
                print("❌ Failed to navigate to jobs page")
                return False
            
            print("✅ Successfully navigated to jobs search page")
            
            # Check if search results are displayed
            self.human_delay(3, 5)
            
            # Look for job results indicators
            job_indicators = [
                ".jobs-search-results__list",
                ".jobs-search-results__list-item",
                ".job-card-container",
                "[data-job-id]"
            ]
            
            results_found = False
            for indicator in job_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                    if elements:
                        print(f"✅ Found job results using selector: {indicator}")
                        results_found = True
                        break
                except:
                    continue
            
            if not results_found:
                print("⚠️ No job results found, trying manual search...")
                return self.manual_job_search()
            
            return True
            
        except Exception as e:
            print(f"❌ Navigation/search failed: {e}")
            return False

    def manual_job_search(self):
        """Manually enter search criteria if URL method fails"""
        print("🔍 Performing manual job search...")
        
        try:
            # Go to jobs page first
            self.driver.get("https://www.linkedin.com/jobs/")
            self.human_delay(3, 5)
            
            # Find and fill keyword search box
            keyword_selectors = [
                "input[aria-label*='Search jobs']",
                "input[placeholder*='Search jobs']",
                ".jobs-search-box__text-input[aria-label*='Search jobs']",
                "#jobs-search-box-keyword-id-ember"
            ]
            
            keyword_box = None
            for selector in keyword_selectors:
                try:
                    keyword_box = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    if keyword_box and keyword_box.is_displayed():
                        break
                except:
                    continue
            
            if keyword_box:
                self.type_like_human(keyword_box, self.keywords)
                print(f"✅ Entered keywords: {self.keywords}")
                self.human_delay(1, 2)
            else:
                print("❌ Could not find keyword search box")
                return False
            
            # Find and fill location search box
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
                self.type_like_human(location_box, self.location)
                print(f"✅ Entered location: {self.location}")
                self.human_delay(1, 2)
            
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
            self.human_delay(5, 8)
            
            # Verify search results
            return self.verify_search_results()
            
        except Exception as e:
            print(f"❌ Manual search failed: {e}")
            return False

    def verify_search_results(self):
        """Verify that search results are displayed"""
        print("🔍 Verifying search results...")
        
        try:
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
                        
                        # Check if results are relevant
                        first_job = elements[0]
                        job_text = first_job.text.lower()
                        
                        # Look for keywords in job listings
                        keyword_found = any(keyword.lower() in job_text for keyword in self.keywords.split())
                        location_found = self.location.lower() in job_text or "remote" in job_text
                        
                        print(f"📊 Relevance check - Keywords: {keyword_found}, Location: {location_found}")
                        return True
                except:
                    continue
            
            print("❌ No job results found")
            return False
            
        except Exception as e:
            print(f"❌ Error verifying results: {e}")
            return False

    def apply_easy_apply_filter(self):
        """Apply Easy Apply filter to show only one-click applications"""
        print("🔧 Applying Easy Apply filter...")

        try:
            current_url = self.driver.current_url

            # Method 1: URL parameter approach
            if "f_LF=f_AL" not in current_url:
                separator = "&" if "?" in current_url else "?"
                new_url = f"{current_url}{separator}f_LF=f_AL"
                print(f"🔗 Applying filter via URL: {new_url}")
                self.driver.get(new_url)
                self.human_delay(5, 8)

                if "f_LF=f_AL" in self.driver.current_url:
                    print("✅ Easy Apply filter applied via URL!")
                    return self.verify_easy_apply_results()

            # Method 2: Click filter buttons
            print("🔍 Looking for filter buttons...")

            # Try to find "All filters" button
            filter_selectors = [
                "//button[contains(@aria-label, 'Show all filters')]",
                "//button[contains(text(), 'All filters')]",
                "//button[contains(text(), 'Filters')]",
                ".artdeco-pill--choice"
            ]

            for selector in filter_selectors:
                try:
                    if selector.startswith("//"):
                        filter_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        filter_button = self.driver.find_element(By.CSS_SELECTOR, selector)

                    if filter_button and filter_button.is_displayed():
                        filter_button.click()
                        print("✅ Clicked filter button")
                        self.human_delay(2, 3)

                        # Look for Easy Apply checkbox
                        easy_apply_selectors = [
                            "//input[@id='f_LF-f_AL']",
                            "//label[contains(text(), 'Easy Apply')]//input",
                            "//span[contains(text(), 'Easy Apply')]//input"
                        ]

                        for ea_selector in easy_apply_selectors:
                            try:
                                checkbox = self.driver.find_element(By.XPATH, ea_selector)
                                if not checkbox.is_selected():
                                    checkbox.click()
                                    print("✅ Easy Apply checkbox selected")

                                # Apply filter
                                apply_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Show results')]")
                                apply_button.click()
                                self.human_delay(3, 5)

                                return self.verify_easy_apply_results()
                            except:
                                continue
                        break
                except:
                    continue

            print("✅ Easy Apply filter process completed")
            return True

        except Exception as e:
            print(f"⚠️ Filter application failed: {e}")
            print("🔄 Continuing without filter...")
            return True

    def verify_easy_apply_results(self):
        """Verify Easy Apply filter is working"""
        print("🔍 Verifying Easy Apply filter results...")

        try:
            self.human_delay(3, 5)

            # Look for Easy Apply indicators in job listings
            easy_apply_indicators = [
                "//span[contains(text(), 'Easy Apply')]",
                "//button[contains(@aria-label, 'Easy Apply')]",
                ".jobs-apply-button"
            ]

            easy_apply_count = 0
            for indicator in easy_apply_indicators:
                try:
                    if indicator.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, indicator)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                    easy_apply_count += len(elements)
                except:
                    continue

            if easy_apply_count > 0:
                print(f"✅ Found {easy_apply_count} Easy Apply jobs!")
                return True
            else:
                print("⚠️ No Easy Apply jobs found, but continuing...")
                return True

        except Exception as e:
            print(f"⚠️ Error verifying Easy Apply results: {e}")
            return True

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

    def apply_to_job(self, job_element):
        """Apply to a single job using profile data"""
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

            # Get job title and company
            job_info = self.extract_job_info()
            print(f"📝 Applying to: {job_info['title']} at {job_info['company']}")

            # Find Easy Apply button using computer vision + traditional methods
            easy_apply_button = self.find_easy_apply_button()

            if not easy_apply_button:
                print("❌ No Easy Apply button found, skipping...")
                return False

            # Click Easy Apply using appropriate method
            if not self.click_easy_apply_button(easy_apply_button):
                print("❌ Failed to click Easy Apply button, skipping...")
                return False

            self.human_delay(3, 5)

            # Check for manual intervention after clicking
            if self.detect_manual_intervention_needed():
                return False

            # Handle application process with profile data
            return self.complete_application_with_profile(job_info)

        except Exception as e:
            print(f"❌ Error applying to job: {e}")
            return False

    def extract_job_info(self):
        """Extract job information from the current job page"""
        job_info = {
            'title': 'Unknown Position',
            'company': 'Unknown Company',
            'location': 'Unknown Location'
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
                "[data-control-name='job_details_topcard_company_url']"
            ]

            for selector in company_selectors:
                try:
                    company_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if company_element and company_element.text.strip():
                        job_info['company'] = company_element.text.strip()
                        break
                except:
                    continue

            # Get location
            location_selectors = [
                ".job-details-jobs-unified-top-card__bullet",
                ".jobs-unified-top-card__bullet"
            ]

            for selector in location_selectors:
                try:
                    location_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if location_element and location_element.text.strip():
                        job_info['location'] = location_element.text.strip()
                        break
                except:
                    continue

        except Exception as e:
            print(f"⚠️ Error extracting job info: {e}")

        return job_info

    def find_easy_apply_button(self):
        """Find the Easy Apply button using computer vision + traditional selectors"""
        print("🔍 Searching for Easy Apply button...")

        # Method 1: Computer Vision (most reliable with your images)
        if self.easy_apply_templates:
            print("🤖 Trying computer vision detection...")
            cv_buttons = self.find_easy_apply_buttons_with_cv()

            if cv_buttons:
                print(f"✅ Found {len(cv_buttons)} Easy Apply buttons with computer vision!")
                # Return the first (highest confidence) button
                return {'type': 'cv', 'data': cv_buttons[0]}

        # Method 2: Traditional CSS/XPath selectors (fallback)
        print("🔍 Trying traditional selector detection...")
        easy_apply_selectors = [
            "//button[contains(@aria-label, 'Easy Apply')]",
            "//button[contains(text(), 'Easy Apply')]",
            ".jobs-apply-button",
            "[data-control-name='jobdetails_topcard_inapply']",
            "//button[contains(@class, 'jobs-apply-button')]",
            "//span[contains(text(), 'Easy Apply')]/parent::button",
            ".jobs-s-apply button",
            "[data-control-name='job_apply_button']"
        ]

        for selector in easy_apply_selectors:
            try:
                if selector.startswith("//"):
                    button = self.driver.find_element(By.XPATH, selector)
                else:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)

                if button and button.is_displayed() and button.is_enabled():
                    print(f"✅ Found Easy Apply button with selector: {selector}")
                    return {'type': 'selenium', 'data': button}
            except:
                continue

        print("❌ No Easy Apply button found with any method")
        return None

    def click_easy_apply_button(self, button_info):
        """Click Easy Apply button based on detection method"""
        if not button_info:
            return False

        try:
            if button_info['type'] == 'cv':
                # Use computer vision coordinates
                return self.click_easy_apply_button_cv(button_info['data'])
            elif button_info['type'] == 'selenium':
                # Use traditional Selenium click
                button_info['data'].click()
                print("✅ Clicked Easy Apply button using Selenium")
                return True
            else:
                print("❌ Unknown button type")
                return False

        except Exception as e:
            print(f"❌ Error clicking Easy Apply button: {e}")
            return False

    def complete_application_with_profile(self, job_info):
        """Complete application using user profile data"""
        try:
            max_steps = 5
            current_step = 0

            while current_step < max_steps:
                current_step += 1
                print(f"📋 Application step {current_step}...")

                # Check for manual intervention
                if self.detect_manual_intervention_needed():
                    return True

                # Fill any form fields with profile data
                self.fill_application_form()

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
                    self.applications_sent += 1  # Count as successful
                    return True
                else:
                    return False

            print("⚠️ Application process exceeded maximum steps")
            return False

        except Exception as e:
            print(f"❌ Error completing application: {e}")
            return False

    def fill_application_form(self):
        """Fill application form fields with profile data"""
        try:
            profile = self.profile

            # Common form fields and their profile mappings
            field_mappings = {
                # Personal information
                'first_name': profile['personal_info']['first_name'],
                'last_name': profile['personal_info']['last_name'],
                'email': profile['personal_info']['email'],
                'phone': profile['personal_info']['phone'],
                'address': f"{profile['personal_info']['address']['street']}, {profile['personal_info']['address']['city']}, {profile['personal_info']['address']['state']}",

                # Professional information
                'current_company': profile['work_experience'][0]['company'] if profile['work_experience'] else '',
                'current_position': profile['work_experience'][0]['position'] if profile['work_experience'] else '',
                'years_experience': '5+',
                'salary_expectation': profile['application_responses']['salary_expectations']['range'],

                # Common questions
                'availability': profile['application_responses']['availability']['start_date'],
                'willing_to_relocate': 'No' if not profile['application_responses']['relocation']['willing_to_relocate'] else 'Yes',
                'authorized_to_work': 'Yes' if profile['application_responses']['work_authorization']['authorized_to_work'] else 'No',
                'visa_sponsorship': 'No' if not profile['application_responses']['work_authorization']['visa_sponsorship_needed'] else 'Yes'
            }

            # Try to fill common input fields
            for field_name, field_value in field_mappings.items():
                self.fill_field_by_patterns(field_name, field_value)

            # Handle dropdowns
            self.fill_dropdown_fields()

        except Exception as e:
            print(f"⚠️ Error filling form: {e}")

    def fill_field_by_patterns(self, field_type, value):
        """Fill field by matching common patterns"""
        if not value:
            return

        patterns = {
            'first_name': ['first_name', 'firstName', 'fname', 'given_name'],
            'last_name': ['last_name', 'lastName', 'lname', 'family_name'],
            'email': ['email', 'email_address', 'emailAddress'],
            'phone': ['phone', 'phone_number', 'phoneNumber', 'mobile'],
            'address': ['address', 'street_address', 'location'],
            'salary_expectation': ['salary', 'expected_salary', 'compensation'],
            'availability': ['availability', 'start_date', 'available_date'],
            'years_experience': ['experience', 'years_experience', 'work_experience']
        }

        if field_type not in patterns:
            return

        for pattern in patterns[field_type]:
            selectors = [
                f"input[name*='{pattern}']",
                f"input[id*='{pattern}']",
                f"input[placeholder*='{pattern}']",
                f"textarea[name*='{pattern}']",
                f"textarea[id*='{pattern}']"
            ]

            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            self.type_like_human(element, str(value))
                            print(f"✅ Filled {field_type}: {value}")
                            return
                except:
                    continue

    def fill_dropdown_fields(self):
        """Fill dropdown fields with profile data"""
        try:
            # Common dropdown mappings
            dropdown_mappings = {
                'experience_level': 'Mid-level',
                'education_level': 'Bachelor\'s degree',
                'work_authorization': 'Yes',
                'visa_sponsorship': 'No'
            }

            for field_type, value in dropdown_mappings.items():
                self.select_dropdown_option(field_type, value)

        except Exception as e:
            print(f"⚠️ Error filling dropdowns: {e}")

    def select_dropdown_option(self, field_type, value):
        """Select option from dropdown"""
        try:
            # Find dropdown by various patterns
            dropdown_selectors = [
                f"select[name*='{field_type}']",
                f"select[id*='{field_type}']",
                f"select[class*='{field_type}']"
            ]

            for selector in dropdown_selectors:
                try:
                    dropdown = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if dropdown.is_displayed():
                        select = Select(dropdown)

                        # Try to select by visible text
                        try:
                            select.select_by_visible_text(value)
                            print(f"✅ Selected {field_type}: {value}")
                            return
                        except:
                            # Try partial match
                            for option in select.options:
                                if value.lower() in option.text.lower():
                                    select.select_by_visible_text(option.text)
                                    print(f"✅ Selected {field_type}: {option.text}")
                                    return
                except:
                    continue

        except Exception as e:
            print(f"⚠️ Error selecting dropdown: {e}")

    def find_submit_button(self):
        """Find submit button"""
        submit_selectors = [
            "//button[contains(@aria-label, 'Submit application')]",
            "//button[contains(text(), 'Submit application')]",
            "//button[contains(text(), 'Submit')]",
            "//button[contains(text(), 'Send application')]",
            "[data-control-name='continue_unify']"
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
        """Main execution with complete job search and application process"""
        print("🚀 LinkedIn Job Applier Starting...")
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
                print("❌ Login failed - stopping automation")
                return

            # Step 2: Navigate and search
            print("\n🔍 Step 2: Performing job search...")
            if not self.navigate_to_jobs_and_search():
                print("❌ Job search failed - stopping automation")
                return

            # Step 3: Verify search results
            print("\n📊 Step 3: Verifying search results...")
            if not self.verify_search_results():
                print("❌ No valid search results found - stopping automation")
                return

            # Step 4: Apply Easy Apply filter
            print("\n🔧 Step 4: Applying Easy Apply filter...")
            self.apply_easy_apply_filter()

            # Step 5: Start job applications
            print(f"\n🚀 Step 5: Starting job application process...")
            print(f"🎯 Target: {self.max_applications} applications")
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
                        print("❌ Too many consecutive failures, stopping automation")
                        break

                    # Try next page
                    if not self.go_to_next_page():
                        print("📄 No more pages available")
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

                    print(f"\n📋 Processing job {i+1}/{len(job_listings)} on page {page_number}")

                    try:
                        success = self.apply_to_job(job_listing)

                        if success:
                            print(f"✅ Application successful! Total: {self.applications_sent}/{self.max_applications}")
                        else:
                            print("❌ Application failed or skipped")

                        # Human-like delay between applications
                        self.human_delay(5, 10)

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
            self.print_final_summary()

        except KeyboardInterrupt:
            print("\n⚠️ Process interrupted by user")
            print(f"📊 Applications sent before interruption: {self.applications_sent}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print(f"📊 Applications sent before error: {self.applications_sent}")
        finally:
            print("\n👋 Closing browser...")
            self.driver.quit()

    def print_final_summary(self):
        """Print final application summary"""
        print("\n" + "=" * 60)
        print("🎉 JOB APPLICATION PROCESS COMPLETE!")
        print("=" * 60)
        print(f"👤 Applicant: {self.profile['personal_info']['full_name']}")
        print(f"🔍 Search Criteria: {self.keywords} in {self.location}")
        print(f"📊 Applications Sent: {self.applications_sent}")
        print(f"🎯 Target Applications: {self.max_applications}")

        if self.max_applications > 0:
            success_rate = (self.applications_sent / self.max_applications) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")

        print(f"📧 Contact Email: {self.email}")
        print(f"📱 Phone: {self.profile['personal_info']['phone']}")

        if self.applications_sent > 0:
            print("\n✅ NEXT STEPS:")
            print("1. Monitor your email for application responses")
            print("2. Check LinkedIn messages for recruiter contacts")
            print("3. Prepare for potential interviews")
            print("4. Update your application tracking spreadsheet")
        else:
            print("\n⚠️ NO APPLICATIONS SENT:")
            print("1. Check if search criteria are too specific")
            print("2. Verify Easy Apply jobs are available")
            print("3. Consider broadening location or keywords")

        print("=" * 60)

if __name__ == '__main__':
    print("🚀 LinkedIn Job Applier")
    print("🎯 Comprehensive automation with user profile integration")
    print("=" * 60)

    try:
        applier = LinkedInJobApplier("user_profile.json")
        applier.run()
    except FileNotFoundError:
        print("❌ user_profile.json not found!")
        print("📝 Please create your user profile file first")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
