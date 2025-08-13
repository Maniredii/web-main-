#!/usr/bin/env python3
"""
Script to fix the PuppeteerBridge class to ensure browser launches correctly
"""

import os
import platform
import json
import logging

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BrowserFix")

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

def update_puppeteer_script():
    """Update the puppeteer_bridge.py script to use the correct browser executable path"""
    browser_path = detect_browser_executable()
    if not browser_path:
        logger.error("Could not find browser executable, cannot update script")
        return False
        
    # Escape backslashes for JavaScript string
    if platform.system() == "Windows":
        browser_path = browser_path.replace("\\", "\\\\")
    
    logger.info(f"Using browser path: {browser_path}")
    
    try:
        # Read the current puppeteer_bridge.py
        with open("puppeteer_bridge.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find the launchBrowser function and update it
        launch_browser_start = content.find("async function launchBrowser()")
        if launch_browser_start == -1:
            logger.error("Could not find launchBrowser function in puppeteer_bridge.py")
            return False
            
        # Find the puppeteer.launch call
        launch_call_start = content.find("const browser = await puppeteer.launch(", launch_browser_start)
        if launch_call_start == -1:
            logger.error("Could not find puppeteer.launch call in puppeteer_bridge.py")
            return False
            
        # Find the end of the launch options
        launch_call_end = content.find("});", launch_call_start)
        if launch_call_end == -1:
            logger.error("Could not find end of puppeteer.launch options")
            return False
            
        # Check if executablePath is already in the options
        launch_options = content[launch_call_start:launch_call_end]
        if "executablePath" in launch_options:
            # Replace the existing executablePath
            logger.info("Updating existing executablePath")
            parts = launch_options.split("executablePath")
            before = parts[0]
            after = parts[1]
            
            # Find the end of the current value
            value_end = after.find(",")
            if value_end == -1:
                value_end = after.find("\n")
            
            if value_end != -1:
                new_launch_options = before + f"executablePath: '{browser_path}'" + after[value_end:]
                new_content = content[:launch_call_start] + new_launch_options + content[launch_call_end:]
            else:
                logger.error("Could not parse existing executablePath")
                return False
        else:
            # Add executablePath to the options
            logger.info("Adding executablePath to launch options")
            insert_point = launch_call_end - 1  # Insert before the closing brace
            new_content = (
                content[:insert_point] + 
                f",\n        executablePath: '{browser_path}'\n    " + 
                content[insert_point:]
            )
        
        # Write the updated content back
        with open("puppeteer_bridge.py", "w", encoding="utf-8") as f:
            f.write(new_content)
            
        logger.info("Successfully updated puppeteer_bridge.py with correct browser path")
        return True
        
    except Exception as e:
        logger.error(f"Error updating puppeteer_bridge.py: {e}")
        return False

def create_launcher_script():
    """Create a simple browser launcher script"""
    browser_path = detect_browser_executable()
    if not browser_path:
        logger.error("Could not find browser executable, cannot create launcher")
        return False
        
    # Escape backslashes for JavaScript string
    if platform.system() == "Windows":
        browser_path = browser_path.replace("\\", "\\\\")
    
    script_content = f"""// simple_linkedin_launcher.js
const puppeteer = require('puppeteer-core');

async function launchLinkedIn() {{
    console.log('Launching browser to LinkedIn...');
    
    try {{
        const browser = await puppeteer.launch({{
            headless: false,
            executablePath: '{browser_path}',
            defaultViewport: null,
            args: [
                '--start-maximized',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        }});
        
        console.log('Browser launched successfully!');
        const page = await browser.newPage();
        
        console.log('Navigating to LinkedIn...');
        await page.goto('https://www.linkedin.com/', {{ waitUntil: 'domcontentloaded', timeout: 60000 }});
        console.log('LinkedIn loaded successfully!');
        
        // Keep the browser open
        // To close it, close the browser window manually
        
    }} catch (error) {{
        console.error('Error launching LinkedIn:', error);
    }}
}}

launchLinkedIn().catch(console.error);
"""
    
    try:
        with open("simple_linkedin_launcher.js", "w", encoding="utf-8") as f:
            f.write(script_content)
            
        logger.info("Created simple_linkedin_launcher.js")
        return True
        
    except Exception as e:
        logger.error(f"Error creating launcher script: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting browser fix")
    
    update_result = update_puppeteer_script()
    logger.info(f"Update puppeteer_bridge.py: {'SUCCESS' if update_result else 'FAILED'}")
    
    launcher_result = create_launcher_script()
    logger.info(f"Create launcher script: {'SUCCESS' if launcher_result else 'FAILED'}")
    
    if update_result and launcher_result:
        logger.info("""
Browser fix completed successfully!

To test the browser launch:
1. Run: node simple_linkedin_launcher.js
   This should open a browser window to LinkedIn

2. Run: python test_browser_launch.py
   This will test both direct browser launch and the PuppeteerBridge

3. Run: python linkedin_job_applier_gui.py
   The GUI should now be able to launch the browser correctly
""")
    else:
        logger.warning("Some fixes failed. Check logs for details.")
