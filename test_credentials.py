#!/usr/bin/env python3
"""
Test LinkedIn credentials from .env file
"""

print("🔍 Testing LinkedIn credentials...")

try:
    from dotenv import load_dotenv
    print("✅ python-dotenv imported successfully")
except ImportError:
    print("❌ python-dotenv not found, installing...")
    import subprocess
    subprocess.run(["pip", "install", "python-dotenv"])
    from dotenv import load_dotenv

# Load environment variables
load_dotenv()
print("✅ .env file loaded")

# Test credentials from .env
email = "tivep27728@devdigs.com"
password = "Mani!8897"

print(f"📧 Email: {email}")
print(f"🔑 Password: {'*' * len(password)}")

# Test basic LinkedIn access
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time
    
    print("🌐 Setting up browser...")
    
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    print("🔐 Testing LinkedIn login...")
    
    # Go to LinkedIn login
    driver.get("https://www.linkedin.com/login")
    time.sleep(3)
    
    # Enter credentials
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'session_key'))
    )
    email_field.clear()
    email_field.send_keys(email)
    
    password_field = driver.find_element(By.NAME, 'session_password')
    password_field.clear()
    password_field.send_keys(password)
    
    print("✅ Credentials entered successfully")
    print("🚀 Attempting login...")
    
    # Submit login
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()
    
    # Wait for result
    time.sleep(8)
    
    current_url = driver.current_url
    page_title = driver.title
    
    print(f"📍 Current URL: {current_url}")
    print(f"📄 Page Title: {page_title}")
    
    # Check login result
    if "feed" in current_url or "linkedin.com/in/" in current_url:
        print("🎉 LOGIN SUCCESSFUL!")
    elif "challenge" in current_url:
        print("⚠️ Security challenge detected - manual intervention needed")
    elif "login" in current_url:
        print("❌ Login failed - still on login page")
    else:
        print("🤔 Unknown result - check manually")
    
    # Take screenshot
    driver.save_screenshot("login_test_result.png")
    print("📸 Screenshot saved as 'login_test_result.png'")
    
    # Keep browser open for manual inspection
    print("🔍 Keeping browser open for 30 seconds for manual inspection...")
    time.sleep(30)
    
    driver.quit()
    print("✅ Test completed!")
    
except Exception as e:
    print(f"❌ Error during test: {e}")
    import traceback
    traceback.print_exc()
