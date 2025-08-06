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
    """Test Z.ai API connection"""
    api_key = os.getenv('ZAI_API_KEY')
    api_url = os.getenv('ZAI_API_URL', 'https://z.ai/api/v1')
    
    print(f"API Key: {api_key[:10]}..." if api_key else "No API key found")
    print(f"API URL: {api_url}")
    
    if not api_key:
        print("❌ ZAI_API_KEY not found in .env file")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "zephyr-7b-beta",
            "messages": [
                {"role": "user", "content": "Hello! Please respond with 'Z.ai API is working correctly' if you can see this message."}
            ],
            "max_tokens": 50,
            "temperature": 0.1
        }
        
        print("Testing Z.ai API connection...")
        response = requests.post(
            f"{api_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"✅ Z.ai API is working! Response: {content}")
            return True
        else:
            print(f"❌ Z.ai API failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Z.ai API: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Z.ai API Integration")
    print("=" * 40)
    
    success = test_zai_api()
    
    if success:
        print("\n✅ Z.ai API integration is working correctly!")
        print("You can now use the unified application with Z.ai support.")
    else:
        print("\n❌ Z.ai API integration failed.")
        print("Please check your API key and network connection.") 