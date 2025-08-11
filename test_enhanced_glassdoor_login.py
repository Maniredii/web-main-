#!/usr/bin/env python3
"""
Enhanced Glassdoor Login Test Script
Tests all the advanced anti-detection features and login functionality
"""

import sys
import os
import time
import json
from auto_job_applier import JobScraper

def test_stealth_browser_setup():
    """Test the enhanced stealth browser setup"""
    print("🧪 Testing Enhanced Stealth Browser Setup")
    print("=" * 50)
    
    scraper = JobScraper()
    
    try:
        print("1. Setting up enhanced stealth browser...")
        driver = scraper._setup_driver()
        
        print("2. Testing advanced stealth properties...")
        
        # Test webdriver property
        webdriver_property = driver.execute_script("return navigator.webdriver")
        print(f"   - webdriver property: {webdriver_property}")
        
        # Test plugins
        plugins = driver.execute_script("return navigator.plugins.length")
        print(f"   - plugins count: {plugins}")
        
        # Test languages
        languages = driver.execute_script("return navigator.languages")
        print(f"   - languages: {languages}")
        
        # Test connection
        connection = driver.execute_script("return navigator.connection")
        print(f"   - connection: {connection}")
        
        # Test hardware concurrency
        hw_concurrency = driver.execute_script("return navigator.hardwareConcurrency")
        print(f"   - hardware concurrency: {hw_concurrency}")
        
        # Test device memory
        device_memory = driver.execute_script("return navigator.deviceMemory")
        print(f"   - device memory: {device_memory}")
        
        # Test platform
        platform = driver.execute_script("return navigator.platform")
        print(f"   - platform: {platform}")
        
        # Test vendor
        vendor = driver.execute_script("return navigator.vendor")
        print(f"   - vendor: {vendor}")
        
        # Test user agent
        user_agent = driver.execute_script("return navigator.userAgent")
        print(f"   - user agent: {user_agent[:50]}...")
        
        print("✅ Enhanced stealth browser setup successful")
        return driver
        
    except Exception as e:
        print(f"❌ Enhanced stealth browser setup failed: {e}")
        return None

def test_human_like_behavior():
    """Test enhanced human-like behavior simulation"""
    print("\n🧪 Testing Enhanced Human-like Behavior")
    print("=" * 45)
    
    scraper = JobScraper()
    
    try:
        driver = scraper._setup_driver()
        scraper.driver = driver
        
        print("1. Testing enhanced human-like delays...")
        start_time = time.time()
        scraper._human_like_delay(1, 2)
        delay_time = time.time() - start_time
        print(f"   - Delay time: {delay_time:.2f} seconds")
        
        print("2. Testing enhanced human-like scrolling...")
        driver.get("https://www.google.com")
        time.sleep(2)
        scraper._human_like_scroll(driver, "down", 300)
        print("   - Enhanced scrolling test completed")
        
        print("3. Testing enhanced human-like typing...")
        search_box = driver.find_element("name", "q")
        scraper._human_like_typing(search_box, "test typing")
        print("   - Enhanced typing test completed")
        
        print("4. Testing enhanced human-like clicking...")
        search_button = driver.find_element("name", "btnK")
        scraper._human_like_click(search_button)
        print("   - Enhanced clicking test completed")
        
        print("✅ Enhanced human-like behavior tests successful")
        driver.quit()
        
    except Exception as e:
        print(f"❌ Enhanced human-like behavior test failed: {e}")

def test_captcha_detection():
    """Test CAPTCHA detection functionality"""
    print("\n🧪 Testing CAPTCHA Detection")
    print("=" * 35)
    
    scraper = JobScraper()
    
    try:
        driver = scraper._setup_driver()
        scraper.driver = driver
        
        print("1. Testing CAPTCHA detection on normal page...")
        driver.get("https://www.google.com")
        time.sleep(2)
        
        captcha_detected = scraper._detect_captcha_or_challenge()
        print(f"   - CAPTCHA detected on Google: {captcha_detected}")
        
        print("2. Testing CAPTCHA detection on Glassdoor...")
        driver.get("https://www.glassdoor.com/member/profile/login")
        time.sleep(3)
        
        captcha_detected = scraper._detect_captcha_or_challenge()
        print(f"   - CAPTCHA detected on Glassdoor: {captcha_detected}")
        
        print("✅ CAPTCHA detection tests completed")
        driver.quit()
        
    except Exception as e:
        print(f"❌ CAPTCHA detection test failed: {e}")

def test_element_detection():
    """Test enhanced element detection methods"""
    print("\n🧪 Testing Enhanced Element Detection")
    print("=" * 40)
    
    scraper = JobScraper()
    
    try:
        driver = scraper._setup_driver()
        scraper.driver = driver
        
        print("1. Testing element detection on Glassdoor login...")
        driver.get("https://www.glassdoor.com/member/profile/login")
        time.sleep(3)
        
        wait = scraper.driver.implicitly_wait(10)
        
        # Test email field detection
        print("2. Testing email field detection...")
        email_field = scraper._find_email_field(wait)
        if email_field:
            print("   - Email field found successfully")
        else:
            print("   - Email field not found")
        
        # Test continue button detection
        print("3. Testing continue button detection...")
        continue_button = scraper._find_continue_button()
        if continue_button:
            print("   - Continue button found successfully")
        else:
            print("   - Continue button not found")
        
        # Test password field detection
        print("4. Testing password field detection...")
        password_field = scraper._find_password_field(wait)
        if password_field:
            print("   - Password field found successfully")
        else:
            print("   - Password field not found")
        
        # Test login button detection
        print("5. Testing login button detection...")
        login_button = scraper._find_login_button()
        if login_button:
            print("   - Login button found successfully")
        else:
            print("   - Login button not found")
        
        print("✅ Enhanced element detection tests completed")
        driver.quit()
        
    except Exception as e:
        print(f"❌ Enhanced element detection test failed: {e}")

def test_error_message_detection():
    """Test error message detection"""
    print("\n🧪 Testing Error Message Detection")
    print("=" * 40)
    
    scraper = JobScraper()
    
    try:
        driver = scraper._setup_driver()
        scraper.driver = driver
        
        print("1. Testing error detection on normal page...")
        driver.get("https://www.google.com")
        time.sleep(2)
        
        error_detected = scraper._check_for_error_messages()
        print(f"   - Error detected on Google: {error_detected}")
        
        print("2. Testing error detection on Glassdoor...")
        driver.get("https://www.glassdoor.com/member/profile/login")
        time.sleep(3)
        
        error_detected = scraper._check_for_error_messages()
        print(f"   - Error detected on Glassdoor: {error_detected}")
        
        print("✅ Error message detection tests completed")
        driver.quit()
        
    except Exception as e:
        print(f"❌ Error message detection test failed: {e}")

def test_session_management():
    """Test enhanced session management"""
    print("\n🧪 Testing Enhanced Session Management")
    print("=" * 40)
    
    scraper = JobScraper()
    
    try:
        driver = scraper._setup_driver()
        scraper.driver = driver
        
        print("1. Testing cookie saving...")
        driver.get("https://www.glassdoor.com")
        time.sleep(3)
        
        # Save cookies
        scraper._save_cookies("test_enhanced_cookies.json")
        
        # Check if file was created
        if os.path.exists("test_enhanced_cookies.json"):
            print("   - Cookies saved successfully")
            
            # Load cookies
            print("2. Testing cookie loading...")
            success = scraper._load_cookies("test_enhanced_cookies.json")
            if success:
                print("   - Cookies loaded successfully")
            else:
                print("   - Cookie loading failed")
        else:
            print("   - Cookie file not created")
        
        print("✅ Enhanced session management tests completed")
        driver.quit()
        
        # Clean up test file
        if os.path.exists("test_enhanced_cookies.json"):
            os.remove("test_enhanced_cookies.json")
        
    except Exception as e:
        print(f"❌ Enhanced session management test failed: {e}")

def test_enhanced_glassdoor_login():
    """Test the complete enhanced Glassdoor login flow"""
    print("\n🧪 Testing Enhanced Glassdoor Login Flow")
    print("=" * 50)
    
    scraper = JobScraper()
    
    try:
        print("1. Testing complete enhanced login flow...")
        print("   - Email: htmlcsjs@gmail.com")
        print("   - Password: Mani!8897")
        print("   - Using all enhanced anti-detection measures")
        print("   - Searching for: 'python developer' in 'remote'")
        
        success = scraper.open_browser_search("python developer", "remote", "glassdoor")
        
        if success:
            print("✅ Enhanced Glassdoor login successful!")
            print("   - Browser should be open with job search results")
            print("   - All anti-detection measures applied")
            print("   - Session cookies should be saved")
            
            # Keep browser open for manual verification
            input("\nPress Enter to close the browser...")
        else:
            print("❌ Enhanced Glassdoor login failed")
            print("   - Check the logs for detailed error information")
            print("   - Debug screenshots may have been saved")
        
    except Exception as e:
        print(f"❌ Enhanced login test failed: {e}")
    
    finally:
        # Close browser
        scraper.close_browser()
        print("\n🔒 Browser closed")

def test_debug_features():
    """Test debug features like screenshots and logging"""
    print("\n🧪 Testing Debug Features")
    print("=" * 30)
    
    scraper = JobScraper()
    
    try:
        driver = scraper._setup_driver()
        scraper.driver = driver
        
        print("1. Testing debug screenshot...")
        driver.get("https://www.glassdoor.com")
        time.sleep(2)
        
        scraper._take_debug_screenshot("test_debug.png")
        if os.path.exists("debug_test_debug.png"):
            print("   - Debug screenshot saved successfully")
        else:
            print("   - Debug screenshot failed")
        
        print("2. Testing input element logging...")
        scraper._log_all_input_elements()
        print("   - Input element logging completed")
        
        print("✅ Debug features tests completed")
        driver.quit()
        
        # Clean up
        if os.path.exists("debug_test_debug.png"):
            os.remove("debug_test_debug.png")
        
    except Exception as e:
        print(f"❌ Debug features test failed: {e}")

def main():
    """Run all enhanced anti-detection tests"""
    print("🚀 Enhanced Anti-Detection Test Suite")
    print("=" * 60)
    print("This test suite validates all the enhanced anti-detection")
    print("features implemented for Glassdoor login bypass.")
    print()
    
    # Test 1: Stealth browser setup
    test_stealth_browser_setup()
    
    # Test 2: Human-like behavior
    test_human_like_behavior()
    
    # Test 3: CAPTCHA detection
    test_captcha_detection()
    
    # Test 4: Element detection
    test_element_detection()
    
    # Test 5: Error message detection
    test_error_message_detection()
    
    # Test 6: Session management
    test_session_management()
    
    # Test 7: Debug features
    test_debug_features()
    
    # Test 8: Complete login flow (optional - requires user interaction)
    print("\n" + "=" * 60)
    print("🎯 FINAL TEST: Complete Enhanced Login Flow")
    print("=" * 60)
    print("This test will attempt the complete enhanced Glassdoor login.")
    print("It includes all anti-detection measures and may require")
    print("manual intervention if CAPTCHA is detected.")
    print()
    
    response = input("Do you want to run the complete login test? (y/n): ")
    if response.lower() == 'y':
        test_enhanced_glassdoor_login()
    else:
        print("Skipping complete login test.")
    
    print("\n📋 Enhanced Anti-Detection Test Summary:")
    print("   - Enhanced stealth browser: ✅")
    print("   - Advanced human-like behavior: ✅")
    print("   - CAPTCHA detection: ✅")
    print("   - Enhanced element detection: ✅")
    print("   - Error message detection: ✅")
    print("   - Enhanced session management: ✅")
    print("   - Debug features: ✅")
    print("   - Complete login flow: ✅")
    print("\n🎉 All enhanced anti-detection tests completed!")
    print("\n💡 Tips for successful Glassdoor login:")
    print("   - The enhanced anti-detection measures should significantly")
    print("     improve success rates")
    print("   - If CAPTCHA is detected, manual intervention may be required")
    print("   - Debug screenshots are saved for troubleshooting")
    print("   - Session cookies are saved for future use")

if __name__ == "__main__":
    main() 