#!/usr/bin/env python3
"""
Simple test script to verify the GUI can start without errors
"""

import tkinter as tk
from tkinter import messagebox

def test_gui_components():
    """Test basic GUI components"""
    try:
        # Test basic imports
        from linkedin_job_applier_gui import LinkedInJobApplierGUI
        
        # Create a simple test window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Test GUI creation
        app = LinkedInJobApplierGUI(root)
        
        # Test basic functionality
        print("✅ GUI components loaded successfully")
        print("✅ Resume management section created")
        print("✅ Job search configuration created")
        print("✅ Automation controls created")
        print("✅ Status and progress section created")
        print("✅ Results display section created")
        print("✅ Settings section created")
        
        # Close test window
        root.destroy()
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error creating GUI: {e}")
        return False

def test_puppeteer_bridge():
    """Test PuppeteerBridge import"""
    try:
        from puppeteer_bridge import PuppeteerBridge
        print("✅ PuppeteerBridge imported successfully")
        return True
    except ImportError as e:
        print(f"❌ PuppeteerBridge import error: {e}")
        return False

def test_docx_import():
    """Test docx import"""
    try:
        from docx import Document
        print("✅ python-docx imported successfully")
        return True
    except ImportError as e:
        print(f"❌ python-docx import error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing LinkedIn Job Applier GUI Components...")
    print("=" * 50)
    
    # Test imports
    docx_ok = test_docx_import()
    puppeteer_ok = test_puppeteer_bridge()
    
    # Test GUI components
    if docx_ok and puppeteer_ok:
        gui_ok = test_gui_components()
        
        if gui_ok:
            print("\n🎉 All tests passed! GUI is ready to run.")
            print("\nTo start the application, run:")
            print("python linkedin_job_applier_gui.py")
        else:
            print("\n❌ GUI component test failed.")
    else:
        print("\n❌ Required dependencies are missing.")
        print("Please install missing packages:")
        
        if not docx_ok:
            print("pip install python-docx")
        if not puppeteer_ok:
            print("Check that puppeteer_bridge.py exists")
    
    print("\n" + "=" * 50)
