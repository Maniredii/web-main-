import json
import subprocess
import os
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PuppeteerBridge:
    def __init__(self):
        self.node_script = "linkedin_bot.js"
        self.is_running = False
        self.chrome_executable_path = self._detect_chrome_path()
    
    def _detect_chrome_path(self):
        """Detect Chrome executable path on Windows"""
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', '')),
            r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USER', '')),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found Chrome at: {path}")
                return path
        
        # Fallback to default path
        default_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        logger.warning(f"Chrome not found in common locations, using default: {default_path}")
        return default_path
        
    def _ensure_node_dependencies(self):
        try:
            if not os.path.exists("package.json"):
                logger.info("Initializing Node.js project...")
                subprocess.run(["npm", "init", "-y"], check=True, capture_output=True, shell=True)
            
            if not os.path.exists("node_modules"):
                logger.info("Installing Puppeteer dependencies...")
                dependencies = [
                    "puppeteer",
                    "puppeteer-extra",
                    "puppeteer-extra-plugin-stealth", 
                    "puppeteer-extra-plugin-anonymize-ua",
                    "random-useragent",
                    "fingerprint-generator",
                    "fingerprint-injector"
                ]
                
                for dep in dependencies:
                    logger.info(f"Installing {dep}...")
                    subprocess.run(["npm", "install", dep], check=True, capture_output=True, shell=True)
                
                logger.info("All Puppeteer dependencies installed successfully!")
            
            return True
            
        except Exception as e:
            logger.error(f"Error installing Node.js dependencies: {e}")
            return False
    
    def _create_puppeteer_script(self):
        script_content = '''const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const AnonymizeUAPlugin = require('puppeteer-extra-plugin-anonymize-ua');
const randomUseragent = require('random-useragent');

// Enhanced stealth setup
puppeteer.use(StealthPlugin());
puppeteer.use(AnonymizeUAPlugin());

async function launchBrowser(executablePath) {
    // Import fingerprinting tools
    const { FingerprintGenerator } = require('fingerprint-generator');
    const { FingerprintInjector } = require('fingerprint-injector');
    
    // Generate a realistic browser fingerprint
    let fingerprint;
    try {
        const fingerprintGenerator = new FingerprintGenerator({
            browsers: [
                { name: "chrome", minVersion: 88 },
                { name: "firefox", minVersion: 91 }
            ],
            devices: ['desktop'],
            operatingSystems: ['windows', 'macos']
        });
        
        fingerprint = fingerprintGenerator.getFingerprint();
        console.log("[DEBUG] Fingerprint generated successfully");
    } catch (error) {
        console.log("[WARN] Fingerprint generation failed, using defaults:", error.message);
        fingerprint = {
            screen: { width: 1920, height: 1080, deviceScaleFactor: 1, hasTouch: false, isLandscape: false },
            userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        };
    }
    
    // Launch browser with enhanced stealth settings
    const browser = await puppeteer.launch({
        executablePath: executablePath,
        headless: false,
        defaultViewport: null, // Use full window size
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--incognito',
            '--disable-application-cache',
            '--disable-cache',
            '--disk-cache-size=0',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-notifications',
            '--disable-popup-blocking',
            '--start-maximized' // Start with maximized window
        ]
    });
    
    console.log("[DEBUG] Browser launched successfully!");

    const page = await browser.newPage();
    
    // Apply the generated fingerprint to the page
    const fingerprintInjector = new FingerprintInjector();
    await fingerprintInjector.attachFingerprintToPage(page, fingerprint);
    
    // Additional stealth measures
    const userAgent = fingerprint.userAgent || randomUseragent.getRandom();
    await page.setUserAgent(userAgent);
    console.log(`[INFO] Using user agent: ${userAgent}`);

    await page.evaluateOnNewDocument(() => {
        // Hide automation indicators
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        
        // Randomize navigator properties
        const getRandomInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
        Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => getRandomInt(4, 16) });
        Object.defineProperty(navigator, 'deviceMemory', { get: () => getRandomInt(4, 32) });
        
        // Mask plugins and mimeTypes
        Object.defineProperty(navigator, 'plugins', { get: () => {
            return [{
                0: { type: "application/pdf", suffixes: "pdf", description: "Portable Document Format" },
                name: "PDF Viewer", filename: "internal-pdf-viewer", description: "Portable Document Format", length: 1
            }];
        }});
    });

    return { browser, page };
}

// Helper function for human-like typing with realistic speed and occasional errors
async function humanType(page, selector, text) {
    // Wait for the element to be ready
    const element = await page.waitForSelector(selector, { timeout: 10000 });
    await element.click({ delay: Math.random() * 100 + 50 });
    
    // Clear any existing text
    await page.evaluate((sel) => document.querySelector(sel).value = '', selector);
    
    // Type with human-like speed and occasional mistakes
    const avgTypingSpeed = Math.floor(Math.random() * 40) + 60; // 60-100ms per character
    
    for (let i = 0; i < text.length; i++) {
        // Occasionally make a typo and then correct it (5% chance)
        if (Math.random() < 0.05 && i < text.length - 1) {
            // Type a wrong character
            const wrongChar = String.fromCharCode(text.charCodeAt(i) + 1);
            await page.type(selector, wrongChar, { delay: avgTypingSpeed });
            
            // Wait a bit before correcting
            await new Promise(resolve => setTimeout(resolve, Math.random() * 300 + 200));
            
            // Delete the wrong character
            await page.keyboard.press('Backspace');
            await new Promise(resolve => setTimeout(resolve, Math.random() * 200 + 100));
        }
        
        // Type the correct character with variable speed
        const charDelay = avgTypingSpeed + Math.floor(Math.random() * 100) - 30; // Vary by ±30ms
        await page.type(selector, text[i], { delay: Math.max(10, charDelay) });
        
        // Occasionally pause while typing (1% chance)
        if (Math.random() < 0.01) {
            await new Promise(resolve => setTimeout(resolve, Math.random() * 500 + 500));
        }
    }
    
    // Pause after completing typing
    await new Promise(resolve => setTimeout(resolve, Math.random() * 300 + 200));
}

// Helper function for human-like scrolling
async function humanScroll(page, distance) {
    // Get viewport height
    const viewportHeight = page.viewport().height;
    
    // Calculate number of steps for smooth scrolling
    const steps = Math.abs(Math.floor(distance / (viewportHeight / 4)));
    const stepSize = distance / steps;
    
    for (let i = 0; i < steps; i++) {
        await page.evaluate((step) => {
            window.scrollBy(0, step);
        }, stepSize);
        
        // Random pause between scroll steps
        await new Promise(resolve => setTimeout(resolve, Math.random() * 100 + 50));
    }
    
    // Final pause after scrolling
    await new Promise(resolve => setTimeout(resolve, Math.random() * 500 + 300));
}

async function linkedinLogin(page, email, password) {
    try {
        console.log("[INFO] Navigating to LinkedIn login...");
        await page.goto('https://www.linkedin.com/login', { waitUntil: 'networkidle2', timeout: 60000 });
        
        console.log("[INFO] LinkedIn login page loaded. Please log in manually if needed.");
        console.log("[INFO] The automation will wait until you complete the login process.");
        
        // Random wait time simulating a human looking at the page
        await new Promise(resolve => setTimeout(resolve, Math.random() * 2000 + 2000));
        
        // Human-like typing for email
        console.log("[INFO] Entering email...");
        await humanType(page, '#username, input[name="session_key"]', email);
        
        // Pause between fields like a human would
        await new Promise(resolve => setTimeout(resolve, Math.random() * 1000 + 500));
        
        // Human-like typing for password
        console.log("[INFO] Entering password...");
        await humanType(page, '#password, input[name="session_password"]', password);
        
        // Random pause before clicking sign in
        await new Promise(resolve => setTimeout(resolve, Math.random() * 1500 + 1000));
        
        // Find and click the sign in button with a natural delay
        const signinButton = await page.waitForSelector('button[type="submit"]', { timeout: 10000 });
        await signinButton.click({ delay: Math.random() * 100 + 50 });
        console.log("[INFO] Sign in clicked");
        
        await new Promise(resolve => setTimeout(resolve, 5000));
        // Avoid duplicate declaration if previously declared
        let currentUrl = page.url();
        console.log("[INFO] Current URL after login:", currentUrl);
        
        // Check for various successful login indicators
        if (currentUrl.includes('feed') || 
            currentUrl.includes('mynetwork') || 
            currentUrl.includes('messaging') ||
            currentUrl.includes('profile') ||
            currentUrl.includes('jobs') ||
            !currentUrl.includes('login')) {
            console.log("[SUCCESS] LinkedIn login successful!");
            return true;
        } else if (currentUrl.includes('checkpoint') || currentUrl.includes('challenge')) {
            console.log("[INFO] Security checkpoint detected - waiting for manual verification...");
            console.log("[INFO] Please complete the puzzle/CAPTCHA manually in the browser...");
            
            // Wait for user to complete the verification
            let attempts = 0;
            const maxAttempts = 60; // Wait up to 5 minutes
            
            while (attempts < maxAttempts) {
                await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
                attempts++;
                
                const newUrl = page.url();
                console.log(`[INFO] Checking URL (attempt ${attempts}/${maxAttempts}): ${newUrl}`);
                
                // Check if we've been redirected to a successful page
                if (newUrl.includes('feed') || 
                    newUrl.includes('mynetwork') || 
                    newUrl.includes('messaging') ||
                    newUrl.includes('profile') ||
                    newUrl.includes('jobs') ||
                    (!newUrl.includes('login') && !newUrl.includes('checkpoint') && !newUrl.includes('challenge'))) {
                    console.log("[SUCCESS] Security verification completed! LinkedIn login successful!");
                    return true;
                }
                
                // Check if we're still on a challenge page
                if (newUrl.includes('checkpoint') || newUrl.includes('challenge')) {
                    console.log(`[INFO] Still on security page... waiting for manual completion (${attempts}/${maxAttempts})`);
                    continue;
                }
            }
            
            console.log("[ERROR] Security verification timeout - please complete manually and try again");
            return false;
        } else {
            console.log("[ERROR] Login may have failed, current URL:", currentUrl);
            return false;
        }
        
    } catch (error) {
        console.log(`[ERROR] LinkedIn login failed: ${error.message}`);
        return false;
    }
}

// Helper function for human-like mouse movement
async function humanMouseMove(page, startX, startY, endX, endY) {
    // Calculate a bezier curve path for natural mouse movement
    const steps = 10;
    
    // Control points for bezier curve - add some randomness
    const cp1x = startX + (endX - startX) * (Math.random() * 0.2 + 0.4);
    const cp1y = startY + (Math.random() * 200 - 100); // Random deviation
    const cp2x = endX - (endX - startX) * (Math.random() * 0.2 + 0.4);
    const cp2y = endY + (Math.random() * 200 - 100); // Random deviation
    
    // Calculate points along the curve
    for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        const t1 = 1 - t;
        
        // Bezier curve formula for coordinates
        const x = t1*t1*t1*startX + 3*t1*t1*t*cp1x + 3*t1*t*t*cp2x + t*t*t*endX;
        const y = t1*t1*t1*startY + 3*t1*t1*t*cp1y + 3*t1*t*t*cp2y + t*t*t*endY;
        
        await page.mouse.move(x, y);
        await new Promise(resolve => setTimeout(resolve, Math.random() * 20 + 10));
    }
}

// Function to simulate human-like clicking
async function humanClick(page, selector) {
    // Wait for the element to be available
    const element = await page.waitForSelector(selector, { timeout: 10000 });
    
    // Get element position
    const boundingBox = await element.boundingBox();
    if (!boundingBox) return false;
    
    // Calculate center point of element
    const centerX = boundingBox.x + boundingBox.width / 2;
    const centerY = boundingBox.y + boundingBox.height / 2;
    
    // Get current mouse position or use a default starting point
    const currentPosition = await page.evaluate(() => {
        return { x: window.innerWidth / 2, y: window.innerHeight / 2 };
    });
    
    // Move mouse in a human-like curve
    await humanMouseMove(
        page, 
        currentPosition.x, 
        currentPosition.y, 
        centerX + (Math.random() * 10 - 5), // Add slight randomness to click position
        centerY + (Math.random() * 10 - 5)
    );
    
    // Pause briefly before clicking
    await new Promise(resolve => setTimeout(resolve, Math.random() * 200 + 50));
    
    // Click with a random delay
    await page.mouse.click(centerX, centerY, { delay: Math.random() * 100 + 30 });
    
    return true;
}

async function navigateToJobs(page, keywords, location) {
    try {
        console.log("[INFO] Navigating to LinkedIn jobs...");
        
        // Wait for any security checkpoints to complete with a natural delay
        await new Promise(resolve => setTimeout(resolve, Math.random() * 3000 + 3000));
        
        // First check if we need to log in
        console.log("[INFO] Checking login status...");
        await page.goto('https://www.linkedin.com/login', { waitUntil: 'networkidle2', timeout: 60000 });
        
        // Wait to see if we get redirected to feed (already logged in)
        await new Promise(resolve => setTimeout(resolve, 5000));
        let currentUrl = page.url();
        
        if (currentUrl.includes('feed') || 
            currentUrl.includes('mynetwork') || 
            currentUrl.includes('messaging') ||
            currentUrl.includes('profile') ||
            currentUrl.includes('jobs')) {
            console.log("[INFO] Already logged in, proceeding to job search...");
        } else {
            console.log("[INFO] Not logged in. Please log in manually in the browser window.");
            console.log("[INFO] Waiting for manual login to complete...");
            
            // Wait for login to complete (up to 5 minutes)
            let attempts = 0;
            const maxAttempts = 60; // 5 minutes
            
            while (attempts < maxAttempts) {
                await new Promise(resolve => setTimeout(resolve, 5000)); // Check every 5 seconds
                attempts++;
                
                const newUrl = page.url();
                console.log(`[INFO] Current URL (attempt ${attempts}/${maxAttempts}): ${newUrl}`);
                
                if (newUrl.includes('feed') || 
                    newUrl.includes('mynetwork') || 
                    newUrl.includes('messaging') ||
                    newUrl.includes('profile') ||
                    newUrl.includes('jobs')) {
                    console.log("[SUCCESS] Login completed successfully!");
                    break;
                }
                
                if (attempts >= maxAttempts) {
                    console.log("[ERROR] Login timeout - please complete login manually");
                    return false;
                }
            }
        }
        
        // Now visit the feed to appear more natural
        await page.goto('https://www.linkedin.com/feed/', { waitUntil: 'networkidle2', timeout: 60000 });
        console.log("[INFO] Visiting LinkedIn feed (more natural behavior)...");
        
        // Scroll down a bit like a human would
        await humanScroll(page, Math.random() * 500 + 300);
        
        // Pause as if reading content
        await new Promise(resolve => setTimeout(resolve, Math.random() * 4000 + 3000));
        
        // Navigate directly to the search URL with parameters to ensure results load
        const encodedKeywords = encodeURIComponent(keywords);
        const encodedLocation = encodeURIComponent(location);
        const searchUrl = `https://www.linkedin.com/jobs/search/?keywords=${encodedKeywords}&location=${encodedLocation}`;
        
        console.log(`[INFO] Navigating to direct search URL: ${searchUrl}`);
        await page.goto(searchUrl, { waitUntil: 'networkidle2', timeout: 60000 });
        
        // Check if we're on the jobs page
        currentUrl = page.url();
        if (!currentUrl.includes('/jobs/')) {
            console.log(`[WARN] Not on jobs page. Current URL: ${currentUrl}`);
            console.log('[INFO] Attempting to navigate to jobs page again...');
            await page.goto('https://www.linkedin.com/jobs/', { waitUntil: 'networkidle2', timeout: 60000 });
            
            // Try the search URL again
            console.log(`[INFO] Trying search URL again: ${searchUrl}`);
            await page.goto(searchUrl, { waitUntil: 'networkidle2', timeout: 60000 });
            currentUrl = page.url();
            console.log(`[INFO] Current URL after retry: ${currentUrl}`);
        }
        
        // Random wait to simulate page reading
        await new Promise(resolve => setTimeout(resolve, Math.random() * 3000 + 2000));
        
        // Take a screenshot for debugging
        await page.screenshot({ path: 'search-results-debug.png' });
        console.log("[DEBUG] Took screenshot of search results page");
        
        // Debug: Log the page content to see what's available
        console.log("[DEBUG] Page title:", await page.title());
        console.log("[DEBUG] Current URL:", page.url());
        
        // Try multiple search input selectors
        let searchInput = null;
        const searchSelectors = [
            'input[placeholder*="Search"]',
            'input[placeholder*="Search jobs"]',
            'input[name="keywords"]',
            'input[data-test="search-input"]'
        ];
        
        for (const selector of searchSelectors) {
            try {
                searchInput = await page.waitForSelector(selector, { timeout: 5000 });
                if (searchInput) {
                    console.log(`[INFO] Found search input with selector: ${selector}`);
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        if (!searchInput) {
            throw new Error("Could not find search input field");
        }
        
        // Use human-like clicking and typing
        await humanClick(page, searchInput.toString());
        await humanType(page, searchInput.toString(), keywords);
        console.log("[INFO] Search keywords entered");
        
        // Try multiple location input selectors
        let locationInput = null;
        const locationSelectors = [
            'input[placeholder*="City"]',
            'input[placeholder*="Location"]',
            'input[placeholder*="Where"]',
            'input[name="location"]'
        ];
        
        for (const selector of locationSelectors) {
            try {
                locationInput = await page.waitForSelector(selector, { timeout: 5000 });
                if (locationInput) {
                    console.log(`[INFO] Found location input with selector: ${selector}`);
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        if (locationInput) {
            // Natural pause between fields
            await new Promise(resolve => setTimeout(resolve, Math.random() * 1000 + 500));
            
            await humanClick(page, locationInput.toString());
            await humanType(page, locationInput.toString(), location);
            console.log("[INFO] Location entered");
        }
        
        // Pause before clicking search like a human would
        await new Promise(resolve => setTimeout(resolve, Math.random() * 1500 + 1000));
        
        // Try multiple search button selectors
        let searchButton = null;
        const buttonSelectors = [
            'button:contains("Search")',
            'button[type="submit"]',
            'button.search',
            'button[data-test="search-button"]'
        ];
        
        for (const selector of buttonSelectors) {
            try {
                searchButton = await page.waitForSelector(selector, { timeout: 5000 });
                if (searchButton) {
                    console.log(`[INFO] Found search button with selector: ${selector}`);
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        if (searchButton) {
            await humanClick(page, searchButton.toString());
            console.log("[INFO] Search button clicked");
        }
        
        // Wait for search results with a natural delay
        await new Promise(resolve => setTimeout(resolve, Math.random() * 3000 + 3000));
        console.log("[SUCCESS] Navigated to jobs with search");
        return true;
        
    } catch (error) {
        console.log(`[ERROR] Failed to navigate to jobs: ${error.message}`);
        return false;
    }
}

async function readJobDescriptions(page) {
    try {
        console.log("[INFO] Reading job descriptions...");
        
        // Natural delay before starting to read jobs
        await new Promise(resolve => setTimeout(resolve, Math.random() * 2000 + 2000));
        
        // Scroll down multiple times to ensure all job listings are loaded
        for (let i = 0; i < 3; i++) {
            await humanScroll(page, Math.random() * 400 + 300);
            await new Promise(resolve => setTimeout(resolve, Math.random() * 1000 + 500));
        }
        
        // Look for job cards with a more comprehensive selector strategy
        const jobCardSelectors = [
            '.jobs-search-results__list-item',
            '.job-search-card',
            '.jobs-search-two-pane__job-card-container',
            'div[data-job-id]'
        ];
        
        let jobCards = [];
        
        for (const selector of jobCardSelectors) {
            jobCards = await page.$$(selector);
            if (jobCards.length > 0) {
                console.log(`[INFO] Found ${jobCards.length} job cards using selector: ${selector}`);
                break;
            }
        }
        
        if (jobCards.length === 0) {
            console.log("[WARN] Could not find job cards with standard selectors, taking screenshot for debugging");
            await page.screenshot({ path: 'jobs-page-debug.png' });
            
            // Try a more generic approach
            jobCards = await page.$$('a[href*="/jobs/view/"]');
            console.log(`[INFO] Found ${jobCards.length} job links using generic selector`);
            
            // If still no results, try even more generic selectors
            if (jobCards.length === 0) {
                console.log("[INFO] Trying more generic selectors and waiting longer...");
                
                // Wait longer for content to load
                await new Promise(resolve => setTimeout(resolve, 5000));
                
                // Try additional selectors
                const additionalSelectors = [
                    '.job-card-container',
                    '.job-card',
                    '.jobs-search-results__list > li',
                    'div[data-occludable-job-id]',
                    'a[href*="/jobs/"]'
                ];
                
                for (const selector of additionalSelectors) {
                    jobCards = await page.$$(selector);
                    if (jobCards.length > 0) {
                        console.log(`[INFO] Found ${jobCards.length} job cards using additional selector: ${selector}`);
                        break;
                    }
                }
                
                // If still nothing, dump page HTML for debugging
                if (jobCards.length === 0) {
                    console.log("[ERROR] Still no job cards found. Dumping page HTML for debugging...");
                    const html = await page.content();
                    const fs = require('fs');
                    fs.writeFileSync('linkedin-jobs-page.html', html);
                    console.log("[DEBUG] Page HTML saved to linkedin-jobs-page.html");
                }
            }
        }
        
        const jobs = [];
        const jobsToProcess = Math.min(jobCards.length, 5);
        
        for (let i = 0; i < jobsToProcess; i++) {
            try {
                // Random delay between processing jobs to appear more human-like
                if (i > 0) {
                    await new Promise(resolve => setTimeout(resolve, Math.random() * 3000 + 2000));
                }
                
                const jobCard = jobCards[i];
                
                // Scroll to the job card with human-like behavior
                await jobCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                await new Promise(resolve => setTimeout(resolve, Math.random() * 1000 + 500));
                
                // Hover over the card first (like a human would)
                const boundingBox = await jobCard.boundingBox();
                if (boundingBox) {
                    const centerX = boundingBox.x + boundingBox.width / 2;
                    const centerY = boundingBox.y + boundingBox.height / 2;
                    await page.mouse.move(centerX, centerY, { steps: 10 });
                    await new Promise(resolve => setTimeout(resolve, Math.random() * 500 + 300));
                }
                
                // Click with a natural delay
                await jobCard.click({ delay: Math.random() * 100 + 50 });
                
                // Wait for job details to load with variable timing
                await new Promise(resolve => setTimeout(resolve, Math.random() * 2000 + 1500));
                
                // Extract job information
                const jobInfo = await page.evaluate(() => {
                    // More comprehensive selectors for job details
                    const titleSelectors = [
                        '.jobs-unified-top-card__job-title',
                        '.job-details-jobs-unified-top-card__job-title',
                        'h1',
                        'h2.t-24'
                    ];
                    
                    const companySelectors = [
                        '.jobs-unified-top-card__company-name',
                        '.job-details-jobs-unified-top-card__company-name',
                        'a[data-test="job-details-company-name"]',
                        '.jobs-details-top-card__company-url'
                    ];
                    
                    const locationSelectors = [
                        '.jobs-unified-top-card__bullet',
                        '.job-details-jobs-unified-top-card__bullet',
                        '.jobs-unified-top-card__workplace-type',
                        'span.jobs-unified-top-card__subtitle-primary-grouping > span:nth-child(2)'
                    ];
                    
                    const descriptionSelectors = [
                        '.jobs-description__content',
                        '.jobs-description-content',
                        'div[data-test="job-description"]',
                        '#job-details'
                    ];
                    
                    // Helper function to find first matching element
                    const findFirstElement = (selectors) => {
                        for (const selector of selectors) {
                            const element = document.querySelector(selector);
                            if (element) return element;
                        }
                        return null;
                    };
                    
                    const titleElement = findFirstElement(titleSelectors);
                    const companyElement = findFirstElement(companySelectors);
                    const locationElement = findFirstElement(locationSelectors);
                    const descriptionElement = findFirstElement(descriptionSelectors);
                    
                    return {
                        title: titleElement ? titleElement.textContent.trim() : 'N/A',
                        company: companyElement ? companyElement.textContent.trim() : 'N/A',
                        location: locationElement ? locationElement.textContent.trim() : 'N/A',
                        description: descriptionElement ? descriptionElement.textContent.trim() : 'N/A',
                        url: window.location.href,
                        timestamp: new Date().toISOString()
                    };
                });
                
                jobs.push(jobInfo);
                console.log(`[INFO] Processed job ${i + 1}: ${jobInfo.title} at ${jobInfo.company}`);
                
                // Simulate reading the job description (scroll through it)
                await humanScroll(page, Math.random() * 400 + 300);
                await new Promise(resolve => setTimeout(resolve, Math.random() * 2000 + 1000));
                await humanScroll(page, Math.random() * 400 + 300);
                
            } catch (error) {
                console.log(`[WARN] Error processing job ${i + 1}: ${error.message}`);
                continue;
            }
        }
        
        console.log(`[SUCCESS] Read ${jobs.length} job descriptions`);
        return jobs;
        
    } catch (error) {
        console.log(`[ERROR] Failed to read job descriptions: ${error.message}`);
        return [];
    }
}

async function main() {
    try {
        const fs = require('fs');
        let credentials;
        
        try {
            const credentialsData = fs.readFileSync('user_credentials.json', 'utf8');
            credentials = JSON.parse(credentialsData);
        } catch (error) {
            console.log("[ERROR] Could not read credentials file:", error.message);
            return;
        }
        
        if (!credentials.linkedin || !credentials.linkedin.email || !credentials.linkedin.password) {
            console.log("[ERROR] LinkedIn credentials not found");
            return;
        }
        
        const { email, password } = credentials.linkedin;
        const keywords = process.argv[2] || "python developer";
        const location = process.argv[3] || "remote";
        const executablePath = process.argv[4] || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
        // Handle resume path that might contain spaces by joining remaining arguments
        const resumePath = process.argv.slice(5).join(" ").replace(/^"|"$/g, "") || "";
        
        console.log(`[INFO] Starting LinkedIn automation: "${keywords}", "${location}"`);
        console.log(`[INFO] Using Chrome executable: ${executablePath}`);
        console.log(`[INFO] Resume path: ${resumePath}`);
        
        const { browser, page } = await launchBrowser(executablePath);
        
        try {
            const loginSuccess = await linkedinLogin(page, email, password);
            if (!loginSuccess) {
                console.log("[ERROR] Login failed, stopping");
                return;
            }
            
            const navigationSuccess = await navigateToJobs(page, keywords, location);
            if (!navigationSuccess) {
                console.log("[ERROR] Failed to navigate to jobs, stopping");
                return;
            }
            
            const jobs = await readJobDescriptions(page);
            fs.writeFileSync('linkedin_jobs.json', JSON.stringify(jobs, null, 2));
            console.log(`[SUCCESS] Saved ${jobs.length} jobs to linkedin_jobs.json`);
            
            console.log("[INFO] Automation complete. Browser will close in 10 seconds...");
            await new Promise(resolve => setTimeout(resolve, 10000));
            
        } finally {
            await browser.close();
        }
        
    } catch (error) {
        console.log(`[ERROR] Automation failed: ${error.message}`);
    }
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = { main, launchBrowser, linkedinLogin, navigateToJobs, readJobDescriptions };
'''
        
        with open(self.node_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        logger.info(f"Created Puppeteer script: {self.node_script}")
    
    def start_linkedin_automation(self, keywords: str, location: str, resume_path: str = None) -> bool:
        try:
            if not self._ensure_node_dependencies():
                return False
            
            self._create_puppeteer_script()
            
            logger.info(f"Starting LinkedIn automation with Puppeteer...")
            logger.info(f"Keywords: {keywords}")
            logger.info(f"Location: {location}")
            
            # Add debugging info
            logger.info(f"Chrome executable path: {self.chrome_executable_path}")
            logger.info(f"Node script path: {self.node_script}")
            
            # Handle resume path with spaces by wrapping in quotes
            resume_arg = f'"{resume_path}"' if resume_path else '""'
            cmd = ["node", self.node_script, keywords, location, self.chrome_executable_path, resume_arg]
            logger.info(f"Running command: {' '.join(cmd)}")
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
            
            self.is_running = True
            
            # Capture output in real-time
            while process.poll() is None:
                output = process.stdout.readline()
                if output:
                    logger.info(f"Puppeteer: {output.strip()}")
                
                error = process.stderr.readline()
                if error:
                    logger.warning(f"Puppeteer Error: {error.strip()}")
                
                time.sleep(0.1)
            
            # Get final output
            stdout, stderr = process.communicate()
            
            # Log all output for debugging
            if stdout:
                logger.info(f"Final stdout: {stdout}")
            if stderr:
                logger.error(f"Final stderr: {stderr}")
            
            if process.returncode == 0:
                logger.info("LinkedIn automation completed successfully!")
                return True
            else:
                logger.error(f"LinkedIn automation failed with return code: {process.returncode}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting LinkedIn automation: {e}")
            return False
        finally:
            self.is_running = False
    
    def get_jobs_from_file(self):
        try:
            jobs_file = "linkedin_jobs.json"
            if os.path.exists(jobs_file):
                with open(jobs_file, 'r', encoding='utf-8') as f:
                    jobs = json.load(f)
                logger.info(f"Loaded {len(jobs)} jobs from Puppeteer automation")
                return jobs
            else:
                logger.warning("No jobs file found from Puppeteer automation")
                return []
        except Exception as e:
            logger.error(f"Error reading jobs file: {e}")
            return []
    
    def stop_automation(self):
        if self.is_running:
            logger.info("Stopping LinkedIn automation...")
            self.is_running = False
    
    def is_automation_running(self) -> bool:
        return self.is_running
