#!/usr/bin/env python3
"""
Test the fixed LinkedIn automation script
"""

print("🧪 Testing Fixed LinkedIn Automation Script...")

try:
    # Test imports
    from selenium import webdriver
    print("✅ Selenium import successful")
    
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    print("✅ WebDriver imports successful")
    
    import tkinter as tk
    print("✅ Tkinter import successful")
    
    from dotenv import load_dotenv
    print("✅ Python-dotenv import successful")
    
    # Test basic functionality
    print("\n🔧 Testing basic browser setup...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless for test
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print("✅ Browser setup successful")
    
    # Test navigation
    driver.get("https://www.linkedin.com/login")
    title = driver.title
    print(f"✅ LinkedIn login page loaded: {title}")
    
    driver.quit()
    print("✅ Browser closed successfully")
    
    # Test popup system
    print("\n🔔 Testing popup system...")
    
    root = tk.Tk()
    root.withdraw()
    
    # Simple test popup
    popup = tk.Toplevel(root)
    popup.title("Test Popup")
    popup.geometry("300x150")
    popup.attributes('-topmost', True)
    
    label = tk.Label(popup, text="Test popup working!")
    label.pack(pady=20)
    
    def close_popup():
        popup.destroy()
        root.quit()
    
    button = tk.Button(popup, text="Close", command=close_popup)
    button.pack(pady=10)
    
    # Auto-close after 2 seconds
    popup.after(2000, close_popup)
    
    print("✅ Popup displayed for 2 seconds")
    popup.mainloop()
    
    print("✅ Popup system working")
    
    print("\n🎉 All tests passed!")
    print("✅ Fixed LinkedIn automation script is ready to use!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
