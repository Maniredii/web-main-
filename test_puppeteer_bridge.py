#!/usr/bin/env python3
"""
Test script for PuppeteerBridge
"""

import time
import logging
from puppeteer_bridge import PuppeteerBridge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_puppeteer_bridge():
    """Test the Puppeteer bridge functionality"""
    
    print("🧪 Testing Puppeteer Bridge...")
    
    # Create bridge instance
    bridge = PuppeteerBridge()
    
    # Test 1: Check if Node.js dependencies can be installed
    print("\n1️⃣ Testing Node.js dependency installation...")
    if bridge._ensure_node_dependencies():
        print("✅ Node.js dependencies check passed")
    else:
        print("❌ Node.js dependencies check failed")
        return False
    
    # Test 2: Test script creation
    print("\n2️⃣ Testing Puppeteer script creation...")
    try:
        bridge._create_puppeteer_script()
        print("✅ Puppeteer script created successfully")
    except Exception as e:
        print(f"❌ Failed to create Puppeteer script: {e}")
        return False
    
    # Test 3: Test automation start (this will open browser)
    print("\n3️⃣ Testing LinkedIn automation start...")
    print("⚠️  This will open a browser window - you can close it manually")
    
    try:
        success = bridge.start_linkedin_automation("python developer", "remote")
        if success:
            print("✅ LinkedIn automation started successfully")
        else:
            print("❌ LinkedIn automation failed to start")
    except Exception as e:
        print(f"❌ Error during automation: {e}")
    
    # Test 4: Check if jobs file was created
    print("\n4️⃣ Testing jobs file reading...")
    jobs = bridge.get_jobs_from_file()
    if jobs:
        print(f"✅ Found {len(jobs)} jobs")
        for i, job in enumerate(jobs[:3]):  # Show first 3 jobs
            print(f"   Job {i+1}: {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
    else:
        print("⚠️  No jobs found (this is normal for first run)")
    
    print("\n🎉 Puppeteer Bridge test completed!")
    return True

if __name__ == "__main__":
    test_puppeteer_bridge()
