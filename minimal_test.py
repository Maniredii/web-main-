print("🤖 Starting minimal test...")

try:
    from selenium import webdriver
    print("✅ Selenium imported successfully")
except ImportError as e:
    print(f"❌ Selenium import failed: {e}")
    exit(1)

try:
    from webdriver_manager.chrome import ChromeDriverManager
    print("✅ WebDriver Manager imported successfully")
except ImportError as e:
    print(f"❌ WebDriver Manager import failed: {e}")
    exit(1)

print("🎉 All imports successful!")
print("🚀 Ready to run LinkedIn automation!")

# Test basic functionality
try:
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless for test
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get("https://www.google.com")
    title = driver.title
    print(f"✅ Browser test successful! Page title: {title}")
    
    driver.quit()
    print("✅ Browser closed successfully")
    
except Exception as e:
    print(f"❌ Browser test failed: {e}")

print("🎯 Test completed!")
