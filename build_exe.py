#!/usr/bin/env python3
"""
Build script for Auto Job Applier
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    """Build the executable using PyInstaller"""
    
    print("🚀 Building Auto Job Applier executable...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller is available")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("auto_job_applier.spec"):
        os.remove("auto_job_applier.spec")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Create a single executable
        "--windowed",  # Don't show console window
        "--name=AutoJobApplier",  # Name of the executable
        "--icon=icon.ico",  # Icon (if available)
        "--add-data=config.json;.",  # Include config file
        "--add-data=my_details.json;.",  # Include user details
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.scrolledtext",
        "--hidden-import=docx",
        "--hidden-import=bs4",
        "--hidden-import=selenium",
        "--hidden-import=requests",
        "--hidden-import=json",
        "--hidden-import=threading",
        "--hidden-import=logging",
        "--hidden-import=datetime",
        "--hidden-import=random",
        "--hidden-import=time",
        "--hidden-import=os",
        "--hidden-import=sys",
        "--hidden-import=subprocess",
        "--hidden-import=typing",
        "auto_job_applier.py"
    ]
    
    # Remove icon option if icon doesn't exist
    if not os.path.exists("icon.ico"):
        cmd = [arg for arg in cmd if arg != "--icon=icon.ico"]
    
    # Remove data files if they don't exist
    if not os.path.exists("config.json"):
        cmd = [arg for arg in cmd if not arg.startswith("--add-data=config.json")]
    if not os.path.exists("my_details.json"):
        cmd = [arg for arg in cmd if not arg.startswith("--add-data=my_details.json")]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        
        # Check if executable was created
        exe_path = Path("dist/AutoJobApplier.exe")
        if exe_path.exists():
            print(f"✅ Executable created: {exe_path.absolute()}")
            print(f"📁 Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        else:
            print("❌ Executable not found in dist folder")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    return True

def create_installer():
    """Create a simple installer script"""
    
    print("\n📦 Creating installer...")
    
    installer_script = """@echo off
echo Installing Auto Job Applier...
echo.

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Auto Job Applier.lnk'); $Shortcut.TargetPath = '%~dp0AutoJobApplier.exe'; $Shortcut.Save()"

echo.
echo Installation complete!
echo You can now run Auto Job Applier from your desktop or the installation folder.
pause
"""
    
    with open("install.bat", "w") as f:
        f.write(installer_script)
    
    print("✅ Installer script created: install.bat")

def main():
    """Main build process"""
    
    print("=" * 60)
    print("Auto Job Applier - Build Script")
    print("=" * 60)
    
    # Check if main script exists
    if not os.path.exists("auto_job_applier.py"):
        print("❌ auto_job_applier.py not found!")
        print("Please run this script from the project directory.")
        return
    
    # Build executable
    if build_executable():
        # Create installer
        create_installer()
        
        print("\n" + "=" * 60)
        print("🎉 Build completed successfully!")
        print("=" * 60)
        print("Files created:")
        print("  - dist/AutoJobApplier.exe (Main executable)")
        print("  - install.bat (Installer script)")
        print("\nTo install:")
        print("  1. Copy the dist folder to your target machine")
        print("  2. Run install.bat to create desktop shortcut")
        print("  3. Or run AutoJobApplier.exe directly")
        print("\nNote: Make sure Ollama is installed and running on the target machine.")
    else:
        print("\n❌ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 