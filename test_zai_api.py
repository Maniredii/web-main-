#!/usr/bin/env python3
"""
Test script to verify Z.ai API integration
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_zai_api():
    """Test Z.ai API with the provided key"""
    api_key = os.getenv('ZAI_API_KEY')
    api_url = os.getenv('ZAI_API_URL', 'https://api.z.ai/v1')
    
    if not api_key:
        print("❌ ZAI_API_KEY not found in .env file")
        return False
    
    print(f"🔑 Testing Z.ai API with key: {api_key[:20]}...")
    print(f"🌐 API URL: {api_url}")
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "zephyr-7b-beta",
            "messages": [
                {"role": "user", "content": "Hello! Please respond with 'Z.ai API is working correctly!'"}
            ],
            "max_tokens": 100,
            "temperature": 0.1
        }
        
        print("📡 Sending test request...")
        response = requests.post(
            f"{api_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"✅ Z.ai API is working!")
            print(f"🤖 Response: {content}")
            return True
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Z.ai API: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Z.ai API Integration")
    print("=" * 50)
    
    success = test_zai_api()
    
    print("=" * 50)
    if success:
        print("🎉 Z.ai API test completed successfully!")
        print("💾 API key has been stored in .env file")
    else:
        print("💥 Z.ai API test failed!")
        print("🔧 Please check your API key and try again") 