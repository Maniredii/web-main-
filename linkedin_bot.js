const puppeteer = require('puppeteer-extra');
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
        const executablePath = process.argv[4] || "C:\Program Files\Google\Chrome\Application\chrome.exe";
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
            
            // Wait for user to see the results
            console.log("[INFO] Job search completed. Browser will stay open for 30 seconds...");
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
