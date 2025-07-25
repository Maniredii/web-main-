#!/usr/bin/env python3
"""
🧪 Test Setup - Verify Everything Works
"""
import os
import sys
import subprocess
from dotenv import load_dotenv

load_dotenv()
sys.path.append('src')

def test_ollama():
    """Test Ollama installation and models"""
    print("🧪 Testing Ollama...")
    
    try:
        # Check version
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama installed: {result.stdout.strip()}")
        else:
            print("❌ Ollama not responding")
            return False
        
        # Check models
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            models = result.stdout.strip()
            if models and 'NAME' in models:
                print("✅ Available models:")
                print(models)
                return True
            else:
                print("⚠️  No models installed")
                print("💡 Run: ollama pull qwen2.5:7b")
                return False
        else:
            print("❌ Cannot list models")
            return False
            
    except FileNotFoundError:
        print("❌ Ollama not found")
        print("📖 Install from: https://ollama.com")
        return False

def test_dependencies():
    """Test Python dependencies"""
    print("\n🧪 Testing Dependencies...")
    
    required = [
        'browser_use',
        'playwright', 
        'langchain',
        'python-dotenv',
        'gradio'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n💡 Install missing packages:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def test_browser():
    """Test browser setup"""
    print("\n🧪 Testing Browser...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browsers = []
            if p.chromium.executable_path:
                browsers.append("Chromium")
            if p.firefox.executable_path:
                browsers.append("Firefox")
            if p.webkit.executable_path:
                browsers.append("WebKit")
            
            if browsers:
                print(f"✅ Browsers available: {', '.join(browsers)}")
                return True
            else:
                print("❌ No browsers found")
                print("💡 Run: python -m playwright install chromium")
                return False
                
    except Exception as e:
        print(f"❌ Browser test failed: {e}")
        return False

def test_api():
    """Test API connection"""
    print("\n🧪 Testing API Connection...")
    
    try:
        from utils import llm_provider
        from langchain_core.messages import HumanMessage
        
        # Try to get LLM
        llm = llm_provider.get_llm_model(
            provider="ollama",
            model_name="qwen2.5:7b",  # Will fallback to available model
            temperature=0.0
        )
        
        print("✅ LLM provider initialized")
        
        # Test simple query
        response = llm.invoke([HumanMessage(content="Say 'Test successful!' and nothing else.")])
        print(f"✅ API Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 SYSTEM TEST")
    print("=" * 30)
    
    tests = [
        ("Ollama", test_ollama),
        ("Dependencies", test_dependencies), 
        ("Browser", test_browser),
        ("API", test_api)
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results[name] = False
    
    print("\n" + "=" * 30)
    print("📊 TEST RESULTS")
    print("=" * 30)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:12} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 30)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("🚀 Ready to run: python job_applier.py")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("💡 Fix the issues above before running job applier")

if __name__ == "__main__":
    main()
