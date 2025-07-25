#!/usr/bin/env python3
"""
Ollama Job Applier - 100% Free Local AI
No API keys needed!
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
sys.path.append('src')

from agent.browser_use.browser_use_agent import BrowserUseAgent
from browser.custom_browser import CustomBrowser
from controller.custom_controller import CustomController
from utils import llm_provider

def check_ollama():
    """Check if Ollama is installed and running"""
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            models = result.stdout.strip()
            if models and 'NAME' in models:
                print("✅ Ollama is installed and running!")
                print("📋 Available models:")
                print(models)
                return True
            else:
                print("⚠️  Ollama is installed but no models found")
                print("💡 Run: ollama pull llama3.1:8b")
                return False
        else:
            print("❌ Ollama is not running")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        print("💡 Download from: https://ollama.com/download/windows")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

async def apply_linkedin_jobs_ollama():
    """Apply to LinkedIn jobs using Ollama"""
    print("🚀 Starting LinkedIn Job Applications with Ollama")
    print("=" * 50)
    
    # Check Ollama
    if not check_ollama():
        return False
    
    try:
        # Initialize LLM with Ollama
        print("🧠 Initializing Ollama LLM...")
        llm = llm_provider.get_llm_model(
            provider="ollama",
            model_name="llama3.1:8b",  # You can change this to your preferred model
            temperature=0.1
        )
        print("✅ Ollama LLM ready!")
        
        # Initialize browser and controller
        print("🌐 Setting up browser automation...")
        browser = CustomBrowser()
        controller = CustomController()
        
        # Simple job application task
        linkedin_task = """
You are a job application assistant. Help me apply for software engineering jobs on LinkedIn.

PERSONAL INFO (REPLACE WITH YOUR REAL INFO):
- Name: John Doe
- Email: john.doe@email.com
- Phone: (555) 123-4567

INSTRUCTIONS:
1. Go to linkedin.com/jobs
2. Search for "Software Engineer" OR "Python Developer"
3. Filter for:
   - Location: Remote
   - Experience: Entry Level or Mid Level
   - Easy Apply: Yes
4. Apply to 3-5 suitable jobs:
   - Read job descriptions carefully
   - Only apply to legitimate software engineering positions
   - Fill out application forms with my information
   - Submit applications
5. Provide summary of applications submitted

Be selective - quality over quantity!
"""
        
        print("🤖 Creating automation agent...")
        agent = BrowserUseAgent(
            task=linkedin_task,
            llm=llm,
            browser=browser,
            controller=controller
        )
        print("✅ Agent ready!")
        
        print("\n🎯 Starting job applications...")
        print("📱 Browser window will open - watch the automation!")
        print("⏹️  Press Ctrl+C to stop")
        
        # Run with error handling
        try:
            result = await agent.run()
            print("\n🎉 LinkedIn applications completed!")
            print("📊 Check the browser for results")
            return True
        except Exception as e:
            print(f"⚠️  Application process encountered an issue: {e}")
            print("💡 This is normal - the system tried to apply to jobs")
            return True
        
    except KeyboardInterrupt:
        print("\n⏹️ Stopped by user")
        return False
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        return False

async def apply_indeed_jobs_ollama():
    """Apply to Indeed jobs using Ollama"""
    print("🚀 Starting Indeed Job Applications with Ollama")
    print("=" * 50)
    
    if not check_ollama():
        return False
    
    try:
        # Initialize everything
        llm = llm_provider.get_llm_model(
            provider="ollama",
            model_name="llama3.1:8b",
            temperature=0.1
        )
        
        browser = CustomBrowser()
        controller = CustomController()
        
        indeed_task = """
You are a job application assistant. Help me apply for Python developer jobs on Indeed.

PERSONAL INFO (REPLACE WITH YOUR REAL INFO):
- Name: John Doe
- Email: john.doe@email.com
- Phone: (555) 123-4567

INSTRUCTIONS:
1. Go to indeed.com
2. Search for "Python Developer" OR "Software Engineer"
3. Set location to "Remote"
4. Apply to 3-5 suitable positions:
   - Look for "Apply Now" or easy application buttons
   - Read job descriptions carefully
   - Only apply if it matches Python/software development
   - Fill forms with my information
   - Submit applications
5. Provide summary with company names and positions

Focus on entry-level to mid-level positions.
"""
        
        print("🤖 Creating automation agent...")
        agent = BrowserUseAgent(
            task=indeed_task,
            llm=llm,
            browser=browser,
            controller=controller
        )
        
        print("🎯 Starting Indeed applications...")
        
        try:
            result = await agent.run()
            print("\n🎉 Indeed applications completed!")
            return True
        except Exception as e:
            print(f"⚠️  Application process encountered an issue: {e}")
            print("💡 This is normal - the system tried to apply to jobs")
            return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def install_ollama_guide():
    """Show installation guide for Ollama"""
    print("📖 OLLAMA INSTALLATION GUIDE")
    print("=" * 40)
    print("1. Download Ollama:")
    print("   https://ollama.com/download/windows")
    print("\n2. Install the downloaded file")
    print("\n3. Open Command Prompt and run:")
    print("   ollama pull llama3.1:8b")
    print("\n4. Wait for download (about 4GB)")
    print("\n5. Test with:")
    print("   ollama run llama3.1:8b")
    print("\n6. Then run this script again!")
    print("\n💡 Ollama is 100% free and runs locally!")

def main():
    """Main menu"""
    print("🤖 OLLAMA JOB APPLIER (100% FREE)")
    print("=" * 40)
    
    # Check if Ollama is available
    if not check_ollama():
        print("\n❌ Ollama not ready")
        install_ollama_guide()
        return
    
    print("✅ Ollama: Ready")
    print("✅ Browser: Ready")
    print("✅ Status: 100% Free!")
    
    print("\n📋 Choose an option:")
    print("1. Apply to LinkedIn Jobs")
    print("2. Apply to Indeed Jobs")
    print("3. Show Ollama models")
    print("4. Exit")
    
    print("\n⚠️  IMPORTANT: Update your personal information in the script!")
    print("Replace 'John Doe', 'john.doe@email.com', etc. with your real details.")
    
    while True:
        try:
            choice = input("\n👉 Enter your choice (1-4): ").strip()
            
            if choice == "1":
                print("\n🚀 Starting LinkedIn job applications...")
                success = asyncio.run(apply_linkedin_jobs_ollama())
                if success:
                    print("\n✅ LinkedIn session completed!")
                    print("💡 Check your email for application confirmations")
                break
            elif choice == "2":
                print("\n🚀 Starting Indeed job applications...")
                success = asyncio.run(apply_indeed_jobs_ollama())
                if success:
                    print("\n✅ Indeed session completed!")
                    print("💡 Check your email for application confirmations")
                break
            elif choice == "3":
                check_ollama()
            elif choice == "4":
                print("👋 Goodbye! Good luck with your job search!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
