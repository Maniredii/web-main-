const puppeteer = require('puppeteer-extra');
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
        } else {
            console.log("[ERROR] Login may have failed, current URL:", currentUrl);
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
        
        // Wait for any security checkpoints to complete
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Navigate to jobs page
        await page.goto('https://www.linkedin.com/jobs/', { waitUntil: 'networkidle2' });
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Debug: Log the page content to see what's available
        console.log("[DEBUG] Page title:", await page.title());
        console.log("[DEBUG] Current URL:", page.url());
        
        // Wait a bit more for dynamic content to load
        await new Promise(resolve => setTimeout(resolve, 3000));
        
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
        
        await searchInput.click();
        await new Promise(resolve => setTimeout(resolve, 1000));
        await searchInput.type(keywords, { delay: 100 });
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
                    console.log(`[INFO] Found search input with selector: ${selector}`);
                    break;
                }
            } catch (e) {
                continue;
            }
        }
        
        if (locationInput) {
            await locationInput.click();
            await new Promise(resolve => setTimeout(resolve, 1000));
            await locationInput.type(location, { delay: 100 });
            console.log("[INFO] Location entered");
        }
        
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
            await searchButton.click();
            console.log("[INFO] Search button clicked");
        }
        
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
