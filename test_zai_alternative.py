import requests

def test_zai_api_alternatives():
    """Test Z.ai API with different endpoints"""
    api_key = "8a6ed1a3c273495a81d7ce90dc9d864e.EAhImlpNo9kMqHkB"
    
    # Try different possible endpoints
    endpoints = [
        "https://api.z.ai/v1",
        "https://api.z.ai",
        "https://z.ai/api/v1",
        "https://z.ai/api",
        "https://api.zai.ai/v1",
        "https://api.zai.ai"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "zephyr-7b-beta",
        "messages": [
            {"role": "user", "content": "Hello!"}
        ],
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    print(f"🔑 Testing Z.ai API with key: {api_key[:20]}...")
    print("🔍 Trying different endpoints...")
    
    for endpoint in endpoints:
        try:
            print(f"\n📡 Testing: {endpoint}")
            response = requests.post(
                f"{endpoint}/chat/completions",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                print(f"✅ SUCCESS! Working endpoint: {endpoint}")
                print(f"🤖 Response: {content}")
                return endpoint
            elif response.status_code == 401:
                print("🔐 401 Unauthorized - API key might be invalid")
            elif response.status_code == 404:
                print("🔍 404 Not Found - Endpoint doesn't exist")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"📄 Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    return None

if __name__ == "__main__":
    print("🚀 Testing Z.ai API Integration (Multiple Endpoints)")
    print("=" * 60)
    
    working_endpoint = test_zai_api_alternatives()
    
    print("=" * 60)
    if working_endpoint:
        print(f"🎉 Z.ai API test completed successfully!")
        print(f"✅ Working endpoint: {working_endpoint}")
        print("💾 Update your .env file with the correct endpoint")
    else:
        print("💥 Z.ai API test failed!")
        print("🔧 The API key might be invalid or the service is not available")
        print("💡 Try checking the Z.ai documentation for the correct API endpoint") 