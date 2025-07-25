#!/usr/bin/env python3
"""
Test Ollama setup for job application system
"""
import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
sys.path.append('src')

def test_ollama_installation():
    """Test if Ollama is installed"""
    print("🧪 Testing Ollama Installation...")
    
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama not responding")
            return False
    except FileNotFoundError:
        print("❌ Ollama not found")
        print("💡 Download from: https://ollama.com/download/windows")
        return False

def test_ollama_models():
    """Test available Ollama models"""
    print("\n🧪 Testing Ollama Models...")
    
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            models = result.stdout.strip()
            if models and 'NAME' in models:
                print("✅ Available models:")
                print(models)
                return True
            else:
                print("⚠️  No models installed")
                print("💡 Install a model with: ollama pull llama3.1:8b")
                return False
        else:
            print("❌ Cannot list models")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ollama_api():
    """Test Ollama API connection"""
    print("\n🧪 Testing Ollama API...")
    
    try:
        from utils import llm_provider
        
        llm = llm_provider.get_llm_model(
            provider="ollama",
            model_name="llama3.1:8b",
            temperature=0.0
        )
        
        print("✅ LLM provider initialized")
        
        # Test a simple query
        from langchain_core.messages import HumanMessage
        
        response = llm.invoke([HumanMessage(content="Say 'Hello from Ollama!' and nothing else.")])
        print(f"✅ API Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

def install_recommended_model():
    """Install recommended model for job applications"""
    print("\n🚀 Installing recommended model...")
    print("This will download llama3.1:8b (about 4GB)")
    
    confirm = input("Continue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Skipped model installation")
        return
    
    try:
        print("📥 Downloading llama3.1:8b...")
        result = subprocess.run(['ollama', 'pull', 'llama3.1:8b'], 
                              capture_output=False, text=True)
        if result.returncode == 0:
            print("✅ Model installed successfully!")
            return True
        else:
            print("❌ Model installation failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🤖 OLLAMA SETUP TEST")
    print("=" * 30)
    
    # Test installation
    if not test_ollama_installation():
        print("\n❌ Ollama not installed")
        print("📖 Installation Guide:")
        print("1. Go to: https://ollama.com/download/windows")
        print("2. Download and install Ollama")
        print("3. Restart your terminal")
        print("4. Run this test again")
        return
    
    # Test models
    has_models = test_ollama_models()
    
    if not has_models:
        print("\n💡 Would you like to install the recommended model?")
        install_recommended_model()
        has_models = test_ollama_models()
    
    if has_models:
        # Test API
        api_works = test_ollama_api()
        
        if api_works:
            print("\n🎉 OLLAMA IS READY!")
            print("=" * 30)
            print("✅ Installation: Working")
            print("✅ Models: Available")
            print("✅ API: Working")
            print("\n🚀 You can now run:")
            print("python3.11 ollama_job_applier.py")
        else:
            print("\n⚠️  Ollama installed but API not working")
            print("💡 Try restarting Ollama service")
    else:
        print("\n❌ No models available")
        print("💡 Install a model first")

if __name__ == "__main__":
    main()
