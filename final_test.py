import requests

def test_zai_final():
    """Final test of Z.ai API with correct endpoint"""
    api_key = "8a6ed1a3c273495a81d7ce90dc9d864e.EAhImlpNo9kMqHkB"
    api_url = "https://z.ai/api/v1"
    
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
    print("🚀 Final Z.ai API Test")
    print("=" * 50)
    
    success = test_zai_final()
    
    print("=" * 50)
    if success:
        print("🎉 Z.ai API test completed successfully!")
        print("✅ The API key is working correctly")
        print("💾 You can now use Z.ai API in your application")
    else:
        print("💥 Z.ai API test failed!")
        print("🔧 Please check your API key and try again") 