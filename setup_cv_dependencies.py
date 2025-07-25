#!/usr/bin/env python3
"""
Setup script for LinkedIn Job Applier with Computer Vision
Installs required dependencies for Easy Apply button detection
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    print("🚀 LinkedIn Job Applier - Computer Vision Setup")
    print("=" * 60)
    print("Installing required dependencies for Easy Apply button detection...")
    print("=" * 60)
    
    # Required packages for computer vision
    packages = [
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.0", 
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "Pillow>=10.0.0",
        "python-dotenv>=1.0.0",
        "groq>=0.4.0",
        "requests>=2.31.0"
    ]
    
    success_count = 0
    total_packages = len(packages)
    
    for package in packages:
        if install_package(package):
            success_count += 1
        print()  # Empty line for readability
    
    print("=" * 60)
    print("📊 INSTALLATION SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully installed: {success_count}/{total_packages} packages")
    
    if success_count == total_packages:
        print("🎉 All dependencies installed successfully!")
        print("\n🚀 You can now run the LinkedIn Job Applier with computer vision:")
        print("   python linkedin_job_applier.py")
        print("\n💡 Make sure your Easy Apply button images are in the same directory:")
        print("   - easy apply image1.png")
        print("   - easy apply image2.webp")
    else:
        print(f"⚠️ {total_packages - success_count} packages failed to install")
        print("Please install them manually or check your Python environment")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
