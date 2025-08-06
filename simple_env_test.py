#!/usr/bin/env python3
"""
Simple test to debug .env file loading
"""

import os
from dotenv import load_dotenv

print("Testing .env file loading...")
print(f"Current directory: {os.getcwd()}")

# Check if .env file exists
env_path = os.path.join(os.getcwd(), '.env')
print(f".env file exists: {os.path.exists(env_path)}")

# Try to load .env
load_dotenv()

# Check environment variables
api_key = os.getenv('ZAI_API_KEY')
api_url = os.getenv('ZAI_API_URL')

print(f"ZAI_API_KEY: {api_key[:10] if api_key else 'None'}...")
print(f"ZAI_API_URL: {api_url}")

# Try reading the file directly
try:
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"Raw .env content:\n{content}")
except Exception as e:
    print(f"Error reading .env file: {e}") 