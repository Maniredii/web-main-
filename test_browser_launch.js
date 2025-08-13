const puppeteer = require('puppeteer');

async function testBrowserLaunch() {
    try {
        console.log("[TEST] Starting browser launch test...");
        
        const browser = await puppeteer.launch({
            headless: false,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        console.log("[TEST] Browser launched successfully!");
        
        const page = await browser.newPage();
        console.log("[TEST] Page created successfully!");
        
        await page.goto('https://www.google.com');
        console.log("[TEST] Navigated to Google successfully!");
        
        // Wait 5 seconds so user can see the browser
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        await browser.close();
        console.log("[TEST] Browser closed successfully!");
        
    } catch (error) {
        console.error("[TEST] Error:", error.message);
        process.exit(1);
    }
}

testBrowserLaunch();
