#!/usr/bin/env python3
"""
Start the job application system
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🚀 Starting Job Application System")
    print("=" * 40)
    
    # Check API keys
    groq_key = os.getenv("GROQ_API_KEY")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    
    print("📋 API Key Status:")
    print(f"✅ Groq: {'Available' if groq_key else 'Not found'}")
    print(f"⚠️  DeepSeek: {'Available (No balance)' if deepseek_key else 'Not found'}")
    
    if not groq_key:
        print("❌ No working API keys found!")
        return
    
    print(f"\n🧠 Using Groq API: {groq_key[:10]}...")
    
    # Add src to path and start web UI
    sys.path.append('src')
    os.chdir('src')
    
    try:
        print("🌐 Starting Web Interface...")
        from webui import main as webui_main
        webui_main()
    except Exception as e:
        print(f"❌ Web interface failed: {e}")
        print("\n🔧 Alternative: Use Python scripts directly")
        print("Run: python3.11 job_applier_example.py")

if __name__ == "__main__":
    main()
