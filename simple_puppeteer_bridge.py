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
                    "puppeteer-extra-plugin-stealth"
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

puppeteer.use(StealthPlugin());

async function launchBrowser(executablePath) {
    console.log("[DEBUG] Launching browser with executablePath:", executablePath);
    
    const browser = await puppeteer.launch({
        executablePath: executablePath,
        headless: false,
        defaultViewport: null,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--start-maximized'
        ]
    });
    
    console.log("[DEBUG] Browser launched successfully!");
    const page = await browser.newPage();
    
    // Simple stealth measures
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
    await page.evaluateOnNewDocument(() => {
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    });

    return { browser, page };
}

async function applyToJobs(page, resumePath) {
    try {
        console.log("[INFO] Scanning for job listings...");
        
        // Wait for job cards to load
        await page.waitForSelector('.jobs-search-results__list-item', { timeout: 30000 });
        
        // Get all job listings
        const jobCards = await page.$$('.jobs-search-results__list-item');
        console.log(`[INFO] Found ${jobCards.length} job listings`);
        
        let appliedCount = 0;
        const maxApplications = 5; // Limit to prevent spam
        
        for (let i = 0; i < Math.min(jobCards.length, maxApplications); i++) {
            try {
                console.log(`[INFO] Processing job ${i + 1}/${Math.min(jobCards.length, maxApplications)}`);
                
                // Click on the job card to open details
                await jobCards[i].click();
                await new Promise(resolve => setTimeout(resolve, 3000));
                
                // Check if there's an apply button
                const applyButton = await page.$('button[aria-label*="Apply"], button[aria-label*="Easy Apply"], .jobs-apply-button');
                
                if (applyButton) {
                    console.log(`[INFO] Apply button found for job ${i + 1}`);
                    
                    // Click apply button
                    await applyButton.click();
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    
                    // Check if we need to upload resume
                    const uploadButton = await page.$('input[type="file"], button[aria-label*="Upload"]');
                    if (uploadButton && resumePath) {
                        console.log(`[INFO] Uploading resume: ${resumePath}`);
                        await uploadButton.uploadFile(resumePath);
                        await new Promise(resolve => setTimeout(resolve, 2000));
                    }
                    
                    // Look for submit button
                    const submitButton = await page.$('button[aria-label*="Submit"], button[aria-label*="Send"], button[type="submit"]');
                    if (submitButton) {
                        await submitButton.click();
                        console.log(`[INFO] Successfully applied to job ${i + 1}`);
                        appliedCount++;
                        await new Promise(resolve => setTimeout(resolve, 3000));
                    } else {
                        console.log(`[WARN] Submit button not found for job ${i + 1}`);
                    }
                    
                    // Close any modals
                    const closeButton = await page.$('button[aria-label*="Close"], button[aria-label*="Dismiss"]');
                    if (closeButton) {
                        await closeButton.click();
                        await new Promise(resolve => setTimeout(resolve, 1000));
                    }
                    
                } else {
                    console.log(`[INFO] No apply button found for job ${i + 1}`);
                }
                
                // Wait between applications
                await new Promise(resolve => setTimeout(resolve, 2000));
                
            } catch (error) {
                console.log(`[WARN] Error processing job ${i + 1}: ${error.message}`);
                continue;
            }
        }
        
        console.log(`[SUCCESS] Applied to ${appliedCount} jobs out of ${Math.min(jobCards.length, maxApplications)} processed`);
        
    } catch (error) {
        console.log(`[ERROR] Job application process failed: ${error.message}`);
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
        const resumePath = process.argv.slice(5).join(" ").replace(/^"|"$/g, "") || "";
        
        console.log(`[INFO] Starting LinkedIn automation: "${keywords}", "${location}"`);
        console.log(`[INFO] Using Chrome executable: ${executablePath}`);
        console.log(`[INFO] Resume path: ${resumePath}`);
        
        const { browser, page } = await launchBrowser(executablePath);
        
        try {
            // Navigate directly to LinkedIn login page
            console.log("[INFO] Navigating to LinkedIn login page...");
            await page.goto('https://www.linkedin.com/login', { waitUntil: 'domcontentloaded', timeout: 60000 });
            console.log("[INFO] Successfully arrived at LinkedIn login page");
            
            // Wait for manual login to complete
            console.log("[INFO] Please log in manually in the browser window...");
            console.log("[INFO] Waiting for login to complete...");
            
            // Wait for login to complete (up to 5 minutes)
            let attempts = 0;
            const maxAttempts = 60; // 5 minutes
            
            while (attempts < maxAttempts) {
                await new Promise(resolve => setTimeout(resolve, 5000)); // Check every 5 seconds
                attempts++;
                
                const currentUrl = page.url();
                console.log(`[INFO] Current URL (attempt ${attempts}/${maxAttempts}): ${currentUrl}`);
                
                if (currentUrl.includes('feed') || 
                    currentUrl.includes('mynetwork') || 
                    currentUrl.includes('messaging') ||
                    currentUrl.includes('profile') ||
                    currentUrl.includes('jobs')) {
                    console.log("[SUCCESS] Login completed successfully!");
                    break;
                }
                
                if (attempts >= maxAttempts) {
                    console.log("[ERROR] Login timeout - please complete login manually");
                    return;
                }
            }
            
                         // Navigate to job search
             console.log("[INFO] Navigating to job search...");
             const encodedKeywords = encodeURIComponent(keywords);
             const encodedLocation = encodeURIComponent(location);
             const searchUrl = `https://www.linkedin.com/jobs/search/?keywords=${encodedKeywords}&location=${encodedLocation}`;
             
             await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
             console.log("[INFO] Arrived at job search page");
             
             // Wait for jobs to load
             await new Promise(resolve => setTimeout(resolve, 5000));
             
             // Start applying to jobs
             console.log("[INFO] Starting job application process...");
             await applyToJobs(page, resumePath);
             
             // Wait for user to see the results
             console.log("[INFO] Job application process completed. Browser will stay open for 30 seconds...");
             await new Promise(resolve => setTimeout(resolve, 30000));
            
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
