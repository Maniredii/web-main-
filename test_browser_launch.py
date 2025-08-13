#!/usr/bin/env python3
"""
Test script to verify browser launching functionality
"""

import os
import platform
import subprocess
import time
import logging

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BrowserTest")

def detect_browser_executable():
    """Detect browser executable path based on platform"""
    system = platform.system()
    logger.info(f"Detecting browser on platform: {system}")
    
    if system == "Windows":
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        ]
        
        for path in candidates:
            if os.path.exists(path):
                logger.info(f"Found browser at: {path}")
                return path
                
    elif system == "Darwin":  # macOS
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
                
    elif system == "Linux":
        candidates = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/snap/bin/chromium",
            "/usr/bin/chromium",
            "/usr/bin/microsoft-edge",
            "/usr/bin/microsoft-edge-stable"
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
    
    logger.error("No browser executable found automatically")
    return None

def test_direct_browser_launch():
    """Test launching browser directly"""
    browser_path = detect_browser_executable()
    if not browser_path:
        logger.error("Could not find browser executable")
        return False
        
    try:
        logger.info(f"Attempting to launch browser directly: {browser_path}")
        process = subprocess.Popen([browser_path, "https://www.linkedin.com"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
        
        # Wait a bit to see if it launches
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            logger.info("Browser launched successfully!")
            return True
        else:
            stdout, stderr = process.communicate()
            logger.error(f"Browser process exited with code: {process.returncode}")
            if stdout:
                logger.error(f"stdout: {stdout.decode('utf-8', errors='ignore')}")
            if stderr:
                logger.error(f"stderr: {stderr.decode('utf-8', errors='ignore')}")
            return False
            
    except Exception as e:
        logger.error(f"Error launching browser: {e}")
        return False

def test_puppeteer_bridge():
    """Test the PuppeteerBridge class"""
    try:
        from puppeteer_bridge import PuppeteerBridge
        
        logger.info("Testing PuppeteerBridge class")
        bridge = PuppeteerBridge()
        
        # Check if Node.js is installed
        try:
            result = subprocess.run(["node", "--version"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   shell=True)
            if result.returncode == 0:
                logger.info(f"Node.js version: {result.stdout.decode('utf-8').strip()}")
            else:
                logger.error("Node.js not found or not working properly")
                return False
        except Exception as e:
            logger.error(f"Error checking Node.js: {e}")
            return False
        
        # Ensure dependencies
        if not bridge._ensure_node_dependencies():
            logger.error("Failed to ensure Node.js dependencies")
            return False
            
        # Create script
        bridge._create_puppeteer_script()
        logger.info("Created Puppeteer script successfully")
        
        # Test launching automation
        logger.info("Testing LinkedIn automation with test keywords")
        success = bridge.start_linkedin_automation("test", "remote")
        
        if success:
            logger.info("PuppeteerBridge test successful!")
            return True
        else:
            logger.error("PuppeteerBridge test failed")
            return False
            
    except Exception as e:
        logger.error(f"Error testing PuppeteerBridge: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting browser launch tests")
    
    # Test direct browser launch
    direct_result = test_direct_browser_launch()
    logger.info(f"Direct browser launch test: {'SUCCESS' if direct_result else 'FAILED'}")
    
    # Test PuppeteerBridge
    bridge_result = test_puppeteer_bridge()
    logger.info(f"PuppeteerBridge test: {'SUCCESS' if bridge_result else 'FAILED'}")
    
    if direct_result and bridge_result:
        logger.info("All tests passed!")
    else:
        logger.warning("Some tests failed. Check logs for details.")
