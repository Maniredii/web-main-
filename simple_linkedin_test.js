const puppeteer = require('puppeteer');

async function simpleLinkedInTest() {
    let browser;
    try {
        console.log("[TEST] Starting simple LinkedIn test...");
        
        // Simple browser launch without complex fingerprinting
        browser = await puppeteer.launch({
            executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            headless: false,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        });
        
        console.log("[TEST] Browser launched successfully!");
        
        const page = await browser.newPage();
        console.log("[TEST] Page created successfully!");
        
        // Navigate to LinkedIn
        console.log("[TEST] Navigating to LinkedIn...");
        await page.goto('https://www.linkedin.com/login', { 
            waitUntil: 'networkidle2', 
            timeout: 60000 
        });
        
        console.log("[TEST] Current URL:", await page.title());
        console.log("[TEST] Page loaded successfully!");
        
        // Wait for user to see the page
        console.log("[TEST] Browser will stay open for 30 seconds...");
        await new Promise(resolve => setTimeout(resolve, 30000));
        
    } catch (error) {
        console.error("[TEST] Error:", error.message);
        console.error("[TEST] Stack trace:", error.stack);
    } finally {
        if (browser) {
            console.log("[TEST] Closing browser...");
            await browser.close();
        }
    }
}

simpleLinkedInTest();
