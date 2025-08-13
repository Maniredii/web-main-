// simple_linkedin_launcher.js
const puppeteer = require('puppeteer-core');

async function launchLinkedIn() {
    console.log('Launching browser to LinkedIn...');
    
    try {
        const browser = await puppeteer.launch({
            headless: false,
            executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            defaultViewport: null,
            args: [
                '--start-maximized',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        });
        
        console.log('Browser launched successfully!');
        const page = await browser.newPage();
        
        console.log('Navigating to LinkedIn...');
        await page.goto('https://www.linkedin.com/', { waitUntil: 'domcontentloaded', timeout: 60000 });
        console.log('LinkedIn loaded successfully!');
        
        // Keep the browser open
        // To close it, close the browser window manually
        
    } catch (error) {
        console.error('Error launching LinkedIn:', error);
    }
}

launchLinkedIn().catch(console.error);
