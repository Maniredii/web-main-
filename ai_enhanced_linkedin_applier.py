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
        """Show reliable manual intervention popup"""
        print(f"🔔 Manual intervention needed: {title}")
        print(f"📋 {message}")
        if instructions:
            print(f"💡 {instructions}")

        # Try multiple popup methods for maximum reliability
        methods = [
            self._show_direct_tkinter_popup,
            self._show_subprocess_popup,
            self._show_messagebox_popup,
            self._fallback_intervention
        ]

        for i, method in enumerate(methods, 1):
            try:
                print(f"🔄 Trying popup method {i}...")
                result = method(title, message, instructions)
                if result:
                    print("✅ User completed manual intervention")
                    return True
            except Exception as e:
                print(f"⚠️ Method {i} failed: {e}")
                continue

        print("❌ All popup methods failed")
        return False

    def _show_direct_tkinter_popup(self, title, message, instructions=""):
        """Direct tkinter popup - most reliable method"""
        import tkinter as tk
        from tkinter import ttk

        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide root window

        # Create popup
        popup = tk.Toplevel(root)
        popup.title("LinkedIn Automation - Manual Action Required")
        popup.geometry("400x250")
        popup.resizable(False, False)

        # Make it modal and always on top
        popup.transient(root)
        popup.grab_set()
        popup.attributes('-topmost', True)
        popup.lift()
        popup.focus_force()

        # Prevent closing without clicking button
        popup.protocol("WM_DELETE_WINDOW", lambda: None)

        # Configure colors
        popup.configure(bg='#ffffff')

        # Header frame
        header_frame = tk.Frame(popup, bg='#0077b5', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        # Title in header
        title_label = tk.Label(header_frame, text=title,
                              font=('Segoe UI', 12, 'bold'),
                              bg='#0077b5', fg='white')
        title_label.pack(expand=True)

        # Content frame
        content_frame = tk.Frame(popup, bg='#ffffff')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Message
        msg_label = tk.Label(content_frame, text=message,
                            font=('Segoe UI', 10),
                            bg='#ffffff', fg='#333333',
                            wraplength=350, justify='center')
        msg_label.pack(pady=(0, 10))

        # Instructions
        if instructions:
            inst_label = tk.Label(content_frame, text=instructions,
                                 font=('Segoe UI', 9),
                                 bg='#ffffff', fg='#666666',
                                 wraplength=350, justify='center')
            inst_label.pack(pady=(0, 15))

        # Button frame
        button_frame = tk.Frame(content_frame, bg='#ffffff')
        button_frame.pack(side='bottom', fill='x')

        # Continue button
        user_clicked = [False]  # Use list to modify from nested function

        def on_continue():
            user_clicked[0] = True
            popup.destroy()
            root.quit()

        continue_btn = tk.Button(button_frame, text="✅ Continue Automation",
                               command=on_continue,
                               font=('Segoe UI', 11, 'bold'),
                               bg='#0077b5', fg='white',
                               padx=30, pady=10,
                               relief='flat',
                               cursor='hand2')
        continue_btn.pack(pady=15)

        # Add hover effects
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
        x = (screen_width - 400) // 2
        y = (screen_height - 250) // 2
        popup.geometry(f"400x250+{x}+{y}")

        # Flash to get attention
        def flash():
            for _ in range(3):
                popup.attributes('-alpha', 0.3)
                popup.update()
                time.sleep(0.1)
                popup.attributes('-alpha', 1.0)
                popup.update()
                time.sleep(0.1)

        popup.after(500, flash)

        # Set focus
        continue_btn.focus_set()

        print("🔔 GUI popup displayed - waiting for user...")

        # Run the popup
        popup.mainloop()

        # Clean up
        try:
            root.destroy()
        except:
            pass

        return user_clicked[0]

    def _show_subprocess_popup(self, title, message, instructions=""):
        """Subprocess-based popup as backup"""
        popup_script = f'''
import tkinter as tk
import sys

def show_popup():
    try:
        root = tk.Tk()
        root.withdraw()

        popup = tk.Toplevel(root)
        popup.title("LinkedIn Automation - Manual Action Required")
        popup.geometry("400x250")
        popup.resizable(False, False)
        popup.attributes('-topmost', True)
        popup.grab_set()
        popup.configure(bg='#ffffff')

        # Header
        header = tk.Frame(popup, bg='#0077b5', height=50)
        header.pack(fill='x')
        header.pack_propagate(False)

        title_label = tk.Label(header, text="""{title}""", font=('Arial', 12, 'bold'),
                              bg='#0077b5', fg='white')
        title_label.pack(expand=True)

        # Content
        content = tk.Frame(popup, bg='#ffffff')
        content.pack(fill='both', expand=True, padx=20, pady=15)

        msg_label = tk.Label(content, text="""{message}""", font=('Arial', 10),
                            bg='#ffffff', fg='#333333', wraplength=350, justify='center')
        msg_label.pack(pady=(0, 10))

        if """{instructions}""":
            inst_label = tk.Label(content, text="""{instructions}""", font=('Arial', 9),
                                 bg='#ffffff', fg='#666666', wraplength=350, justify='center')
            inst_label.pack(pady=(0, 15))

        def on_continue():
            popup.destroy()
            root.quit()
            sys.exit(0)

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

    except Exception as e:
        print(f"Popup error: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    show_popup()
'''

        try:
            with open('temp_popup.py', 'w') as f:
                f.write(popup_script)

            result = subprocess.run([sys.executable, 'temp_popup.py'],
                                  capture_output=True, text=True, timeout=300)

            os.remove('temp_popup.py')
            return result.returncode == 0

        except Exception as e:
            try:
                os.remove('temp_popup.py')
            except:
                pass
            raise e

    def _show_messagebox_popup(self, title, message, instructions=""):
        """Simple messagebox as backup"""
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        full_message = f"{message}\n\n{instructions}" if instructions else message

        result = messagebox.showinfo(
            "LinkedIn Automation - Manual Action Required",
            full_message
        )

        root.destroy()
        return True

    def _fallback_intervention(self, title, message, instructions=""):
        """Fallback text-based intervention"""
        print("\n" + "="*60)
        print(f"🚨 MANUAL INTERVENTION REQUIRED: {title}")
        print("="*60)
        print(f"📋 {message}")
        if instructions:
            print(f"💡 {instructions}")
        print("="*60)
        print("⌨️ Press ENTER when completed...")
        print("="*60)
        
        try:
            input()
            return True
        except KeyboardInterrupt:
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

    def run(self):
        """Main AI-enhanced execution"""
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

            print(f"\n🎉 AI-Enhanced Setup Complete!")
            print(f"📊 Ready to apply to {self.keywords} jobs")
            print(f"🎯 Target: {self.max_applications} applications")
            print(f"🤖 AI Status: {'Active' if self.use_ai else 'Inactive'}")

            print("\n🔍 Keeping browser open for inspection...")
            time.sleep(60)

        except KeyboardInterrupt:
            print("\n⚠️ Process interrupted")
        except Exception as e:
            print(f"❌ Error: {e}")
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
