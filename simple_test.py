#!/usr/bin/env python3
"""
Simple LinkedIn Test Script
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_linkedin():
    print("🤖 Simple LinkedIn Test Starting...")
    
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Auto-manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("🌐 Opening LinkedIn...")
        driver.get("https://www.linkedin.com/login")
        time.sleep(3)
        
        print("🔐 Logging in...")
        email_field = driver.find_element(By.NAME, 'session_key')
        email_field.send_keys("htmlcsjs@gmail.com")
        
        password_field = driver.find_element(By.NAME, 'session_password')
        password_field.send_keys("Mani!8897")
        
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        print("⏳ Waiting for login...")
        time.sleep(5)
        
        print("🔍 Going to jobs page...")
        driver.get("https://www.linkedin.com/jobs/search/?keywords=Python%20Developer&location=Remote&f_LF=f_AL")
        time.sleep(5)
        
        print("📊 Checking for job listings...")
        
        # Try different selectors
        selectors = [
            ".jobs-search-results__list-item",
            ".job-card-container", 
            "[data-job-id]",
            ".scaffold-layout__list-item",
            "[class*='job']"
        ]
        
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"   {selector}: {len(elements)} elements found")
        
        # Take screenshot
        driver.save_screenshot("linkedin_test.png")
        print("📸 Screenshot saved as 'linkedin_test.png'")
        
        # Check page info
        print(f"📍 Current URL: {driver.current_url}")
        print(f"📄 Page Title: {driver.title}")
        
        # Wait for user to see
        print("⏳ Keeping browser open for 30 seconds...")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("👋 Closing browser...")
        driver.quit()

if __name__ == '__main__':
    test_linkedin()
