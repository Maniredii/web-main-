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
                    "random-useragent"
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

puppeteer.use(StealthPlugin());
puppeteer.use(AnonymizeUAPlugin());

async function launchBrowser() {
    const browser = await puppeteer.launch({
        headless: false,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--incognito',
            '--disable-application-cache',
            '--disable-cache',
            '--disk-cache-size=0'
        ],
        defaultViewport: {
            width: Math.floor(Math.random() * (1920 - 1366 + 1) + 1366),
            height: Math.floor(Math.random() * (1080 - 768 + 1) + 768)
        }
    });

    const page = await browser.newPage();
    const userAgent = randomUseragent.getRandom();
    await page.setUserAgent(userAgent);
    console.log(`[INFO] Using user agent: ${userAgent}`);

    await page.evaluateOnNewDocument(() => {
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    });

    return { browser, page };
}

async function linkedinLogin(page, email, password) {
    try {
        console.log("[INFO] Navigating to LinkedIn login...");
        await page.goto('https://www.linkedin.com/login', { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const emailField = await page.waitForSelector('#username, input[name="session_key"]', { timeout: 10000 });
        await emailField.type(email, { delay: 100 });
        console.log("[INFO] Email entered");
        
        const passwordField = await page.waitForSelector('#password, input[name="session_password"]', { timeout: 10000 });
        await passwordField.type(password, { delay: 100 });
        console.log("[INFO] Password entered");
        
        const signinButton = await page.waitForSelector('button[type="submit"]', { timeout: 10000 });
        await signinButton.click();
        console.log("[INFO] Sign in clicked");
        
        await new Promise(resolve => setTimeout(resolve, 5000));
        const currentUrl = page.url();
        
        if (currentUrl.includes('feed') || currentUrl.includes('mynetwork')) {
            console.log("[SUCCESS] LinkedIn login successful!");
            return true;
        } else {
            console.log("[ERROR] Login may have failed");
            return false;
        }
        
    } catch (error) {
        console.log(`[ERROR] LinkedIn login failed: ${error.message}`);
        return false;
    }
}

async function navigateToJobs(page, keywords, location) {
    try {
        console.log("[INFO] Navigating to LinkedIn jobs...");
        await page.goto('https://www.linkedin.com/jobs/', { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const searchInput = await page.waitForSelector('input[placeholder*="Search"]', { timeout: 10000 });
        await searchInput.type(keywords, { delay: 100 });
        
        const locationInput = await page.waitForSelector('input[placeholder*="City"]', { timeout: 10000 });
        await locationInput.type(location, { timeout: 10000 });
        
        const searchButton = await page.waitForSelector('button:contains("Search")', { timeout: 10000 });
        await searchButton.click();
        
        await new Promise(resolve => setTimeout(resolve, 5000));
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
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const jobCards = await page.$$('.jobs-search-results__list-item');
        console.log(`[INFO] Found ${jobCards.length} job cards`);
        
        const jobs = [];
        const jobsToProcess = Math.min(jobCards.length, 5);
        
        for (let i = 0; i < jobsToProcess; i++) {
            try {
                const jobCard = jobCards[i];
                await jobCard.scrollIntoView();
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                await jobCard.click();
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                const jobInfo = await page.evaluate(() => {
                    const titleElement = document.querySelector('.jobs-unified-top-card__job-title, h1');
                    const companyElement = document.querySelector('.jobs-unified-top-card__company-name');
                    const descriptionElement = document.querySelector('.jobs-description__content');
                    
                    return {
                        title: titleElement ? titleElement.textContent.trim() : 'N/A',
                        company: companyElement ? companyElement.textContent.trim() : 'N/A',
                        description: descriptionElement ? descriptionElement.textContent.trim() : 'N/A',
                        url: window.location.href
                    };
                });
                
                jobs.push(jobInfo);
                console.log(`[INFO] Processed job ${i + 1}: ${jobInfo.title}`);
                await new Promise(resolve => setTimeout(resolve, 2000));
                
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
        
        console.log(`[INFO] Starting LinkedIn automation: "${keywords}", "${location}"`);
        
        const { browser, page } = await launchBrowser();
        
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
    
    def start_linkedin_automation(self, keywords: str, location: str) -> bool:
        try:
            if not self._ensure_node_dependencies():
                return False
            
            self._create_puppeteer_script()
            
            logger.info(f"Starting LinkedIn automation with Puppeteer...")
            logger.info(f"Keywords: {keywords}")
            logger.info(f"Location: {location}")
            
            process = subprocess.Popen([
                "node", self.node_script, keywords, location
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
            
            self.is_running = True
            
            while process.poll() is None:
                output = process.stdout.readline()
                if output:
                    logger.info(f"Puppeteer: {output.strip()}")
                
                error = process.stderr.readline()
                if error:
                    logger.warning(f"Puppeteer Error: {error.strip()}")
                
                time.sleep(0.1)
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                logger.info("LinkedIn automation completed successfully!")
                return True
            else:
                logger.error(f"LinkedIn automation failed with return code: {process.returncode}")
                if stderr:
                    logger.error(f"Error output: {stderr}")
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
