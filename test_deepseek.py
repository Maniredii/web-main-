#!/usr/bin/env python3
"""
Test DeepSeek API connection
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
sys.path.append('src')

def test_deepseek():
    """Test DeepSeek API connection"""
    try:
        print("🧪 Testing DeepSeek API connection...")
        
        # Test if API key is set
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("❌ DEEPSEEK_API_KEY not found in environment")
            return False
        
        print(f"✅ API key found: {api_key[:10]}...")
        
        # Test LLM initialization
        from utils import llm_provider
        
        llm = llm_provider.get_llm_model(
            provider="deepseek",
            model_name="deepseek-chat",
            temperature=0.0
        )
        
        print("✅ LLM initialized successfully")
        
        # Test a simple query
        from langchain_core.messages import HumanMessage
        
        response = llm.invoke([HumanMessage(content="Say 'Hello from DeepSeek!' and nothing else.")])
        print(f"✅ API Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_deepseek()
    if success:
        print("\n🎉 DeepSeek is working perfectly!")
        print("You can now use the job application system.")
    else:
        print("\n💥 DeepSeek test failed. Please check your API key.")
