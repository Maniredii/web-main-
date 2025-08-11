#!/usr/bin/env python3
"""
Test script for browser functionality
Tests the browser opening and Glassdoor login features
"""

import sys
import os
import time
from auto_job_applier import JobScraper

def test_browser_functionality():
    """Test browser opening for different platforms"""
    scraper = JobScraper()
    
    print("🧪 Testing Browser Functionality")
    print("=" * 50)
    
    # Test Indeed
    print("\n1. Testing Indeed browser opening...")
    try:
        success = scraper.open_browser_search("python developer", "remote", "indeed")
        if success:
            print("✅ Indeed browser opened successfully")
            time.sleep(3)  # Wait to see the page
        else:
            print("❌ Failed to open Indeed browser")
    except Exception as e:
        print(f"❌ Error opening Indeed: {e}")
    
    # Close browser
    scraper.close_browser()
    time.sleep(2)
    
    # Test LinkedIn
    print("\n2. Testing LinkedIn browser opening...")
    try:
        success = scraper.open_browser_search("python developer", "remote", "linkedin")
        if success:
            print("✅ LinkedIn browser opened successfully")
            time.sleep(3)  # Wait to see the page
        else:
            print("❌ Failed to open LinkedIn browser")
    except Exception as e:
        print(f"❌ Error opening LinkedIn: {e}")
    
    # Close browser
    scraper.close_browser()
    time.sleep(2)
    
    # Test Glassdoor with login
    print("\n3. Testing Glassdoor browser opening with login...")
    try:
        success = scraper.open_browser_search("python developer", "remote", "glassdoor")
        if success:
            print("✅ Glassdoor browser opened and logged in successfully")
            time.sleep(5)  # Wait longer to see the logged-in state
        else:
            print("❌ Failed to open Glassdoor browser")
    except Exception as e:
        print(f"❌ Error opening Glassdoor: {e}")
    
    # Close browser
    scraper.close_browser()
    
    print("\n🎉 Browser functionality test completed!")

if __name__ == "__main__":
    test_browser_functionality() 