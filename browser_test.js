// browser_test.js - Simple script to test browser launching
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const os = require('os');
const path = require('path');

const URL = 'https://www.linkedin.com/';

function fileExists(p) {
  try { return fs.existsSync(p); } catch { return false; }
}

function detectBrowserExecutable() {
  const platform = os.platform();
  console.log(`[launcher] Detecting browser on platform: ${platform}`);

  if (platform === 'win32') {
    const candidates = [
      // Chrome
      'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
      // Edge
      'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
      'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
    ];
    
    for (const p of candidates) {
      if (fileExists(p)) {
        console.log(`[launcher] Found browser at: ${p}`);
        return p;
      }
    }
  }

  if (platform === 'darwin') { // macOS
    const chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
    const edge = '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge';
    if (fileExists(chrome)) return chrome;
    if (fileExists(edge)) return edge;
  }

  // Linux
  const linuxBins = [
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable',
    '/snap/bin/chromium',
    '/usr/bin/chromium',
    '/usr/bin/microsoft-edge',
    '/usr/bin/microsoft-edge-stable'
  ];
  for (const p of linuxBins) if (fileExists(p)) return p;

  console.log('[launcher] No browser executable found automatically');
  return null;
}

async function launchBrowser() {
  console.log('[launcher] Starting browser launch test...');
  
  // Detect browser executable
  const executablePath = detectBrowserExecutable();
  if (!executablePath) {
    console.error('[launcher] ERROR: Could not find Chrome or Edge on this system.');
    console.error('[launcher] Please install Chrome or Edge, or set the correct path manually.');
    return;
  }

  try {
    console.log(`[launcher] Launching browser at: ${executablePath}`);
    const browser = await puppeteer.launch({
      headless: false,
      executablePath,
      defaultViewport: null,
      args: [
        '--start-maximized',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-blink-features=AutomationControlled'
      ]
    });
    
    console.log('[launcher] Browser launched successfully!');
    const page = await browser.newPage();
    console.log('[launcher] New page created');
    
    console.log(`[launcher] Navigating to ${URL}`);
    await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
    console.log('[launcher] Page loaded successfully');
    
    // Keep the window open for 30 seconds
    console.log('[launcher] Keeping browser open for 30 seconds...');
    await new Promise(r => setTimeout(r, 30000));
    
    await browser.close();
    console.log('[launcher] Browser closed');
    
  } catch (e) {
    console.error('[launcher] ERROR launching browser:', e);
  }
}

// Run the test
launchBrowser().catch(err => {
  console.error('[launcher] Fatal error:', err);
});
