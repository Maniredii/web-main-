#!/usr/bin/env python3
"""
🚀 Llama 3 Setup Script for Job Automation
Helps you set up the best Llama 3 model for job automation
"""

import subprocess
import sys
import time

def run_command(command, description):
    """Run a command and show progress"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def check_ollama_installed():
    """Check if Ollama is installed"""
    print("🔍 Checking if Ollama is installed...")
    try:
        result = subprocess.run("ollama --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama is not installed or not in PATH")
            return False
    except:
        print("❌ Ollama is not installed")
        return False

def list_available_models():
    """List available Llama 3 models"""
    print("\n📋 Available Llama 3 Models:")
    print("=" * 50)
    print("1. llama3.2:3b    - Fast, lightweight (3B parameters)")
    print("2. llama3.2:7b    - ⭐ RECOMMENDED ⭐ (7B parameters)")
    print("3. llama3.2:70b   - Highest quality (70B parameters)")
    print("4. llama3.2:8b    - Good balance (8B parameters)")
    print("5. llama3.2:1b    - Very fast (1B parameters)")
    print("=" * 50)

def get_model_choice():
    """Get user's model choice"""
    while True:
        choice = input("\n🎯 Which Llama 3 model would you like to use? (1-5): ").strip()
        models = {
            "1": "llama3.2:3b",
            "2": "llama3.2:7b", 
            "3": "llama3.2:70b",
            "4": "llama3.2:8b",
            "5": "llama3.2:1b"
        }
        if choice in models:
            return models[choice]
        print("❌ Please enter a number between 1-5")

def test_model(model_name):
    """Test if the model works"""
    print(f"\n🧪 Testing {model_name}...")
    test_prompt = "Hello! Please respond with 'Llama 3 is working correctly' if you can see this message."
    
    try:
        import requests
        payload = {
            "model": model_name,
            "prompt": test_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 50
            }
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("response", "")
            print(f"✅ {model_name} is working! Response: {content}")
            return True
        else:
            print(f"❌ {model_name} test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing {model_name}: {e}")
        return False

def main():
    print("🚀 Llama 3 Setup for Job Automation")
    print("=" * 50)
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("\n📥 Please install Ollama first:")
        print("1. Go to https://ollama.ai")
        print("2. Download and install Ollama")
        print("3. Run this script again")
        return
    
    # Show available models
    list_available_models()
    
    # Get user choice
    model_name = get_model_choice()
    
    print(f"\n🎯 You selected: {model_name}")
    
    # Check if model is already downloaded
    print(f"\n🔍 Checking if {model_name} is already downloaded...")
    if run_command(f"ollama list | grep {model_name}", f"Checking {model_name}"):
        print(f"✅ {model_name} is already available!")
    else:
        # Download the model
        print(f"\n📥 Downloading {model_name}...")
        print("⚠️  This may take several minutes depending on your internet speed")
        print("💡 Model sizes: 3B (~2GB), 7B (~4GB), 70B (~40GB)")
        
        if run_command(f"ollama pull {model_name}", f"Downloading {model_name}"):
            print(f"✅ {model_name} downloaded successfully!")
        else:
            print(f"❌ Failed to download {model_name}")
            return
    
    # Test the model
    if test_model(model_name):
        print(f"\n🎉 {model_name} is ready to use!")
        print(f"\n📝 Next steps:")
        print(f"1. Run: python unified_job_automation_app.py")
        print(f"2. Open: http://localhost:5000")
        print(f"3. Start automating your job applications!")
    else:
        print(f"\n❌ {model_name} is not working properly")
        print("Please check your Ollama installation")

if __name__ == "__main__":
    main() 