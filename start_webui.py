#!/usr/bin/env python3
"""
Start the web UI with proper environment loading
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append('src')

# Change to src directory
os.chdir('src')

# Import and run the web UI
try:
    from webui import main
    print("🚀 Starting Web UI with Groq configuration...")
    print(f"✅ Groq API Key loaded: {os.getenv('GROQ_API_KEY')[:10] if os.getenv('GROQ_API_KEY') else 'Not found'}...")
    main()
except Exception as e:
    print(f"❌ Error starting web UI: {e}")
    print("You can still use the Python scripts directly!")
