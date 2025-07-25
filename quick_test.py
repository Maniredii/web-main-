#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("Testing environment...")
print(f"Python version: {os.sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"GROQ_API_KEY set: {'Yes' if os.getenv('GROQ_API_KEY') else 'No'}")
if os.getenv('GROQ_API_KEY'):
    print(f"API Key: {os.getenv('GROQ_API_KEY')[:10]}...")

# Test basic import
try:
    import sys
    sys.path.append('src')
    from utils import llm_provider
    print("✅ Import successful")
except Exception as e:
    print(f"❌ Import failed: {e}")

print("Test complete!")
