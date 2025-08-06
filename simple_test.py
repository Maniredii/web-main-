import os
from dotenv import load_dotenv

print("Testing environment variable loading...")

# Try to load .env file
try:
    load_dotenv()
    print("✅ .env file loaded successfully")
except Exception as e:
    print(f"❌ Error loading .env: {e}")

# Check if variables are loaded
api_key = os.getenv('ZAI_API_KEY')
api_url = os.getenv('ZAI_API_URL')

print(f"🔑 API Key: {api_key[:20] if api_key else 'None'}...")
print(f"🌐 API URL: {api_url}")

if api_key:
    print("✅ API key found in environment")
else:
    print("❌ API key not found") 