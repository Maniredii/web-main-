#!/usr/bin/env python3
"""
Test Groq API connection
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
sys.path.append('src')

from utils import llm_provider

def test_groq():
    """Test Groq API connection"""
    try:
        print("🧪 Testing Groq API connection...")
        
        # Test if API key is set
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ GROQ_API_KEY not found in environment")
            return False
        
        print(f"✅ API key found: {api_key[:10]}...")
        
        # Test LLM initialization
        llm = llm_provider.get_llm_model(
            provider="groq",
            model_name="llama-3.3-70b-versatile",
            temperature=0.0
        )
        
        print("✅ LLM initialized successfully")
        
        # Test a simple query
        from langchain_core.messages import HumanMessage
        
        response = llm.invoke([HumanMessage(content="Say 'Hello from Groq!' and nothing else.")])
        print(f"✅ API Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_groq()
    if success:
        print("\n🎉 Groq is working perfectly!")
        print("You can now use the job application system.")
    else:
        print("\n💥 Groq test failed. Please check your API key.")
