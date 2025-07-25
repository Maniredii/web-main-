#!/usr/bin/env python3
"""
🤖 Ultimate Job Applier - Lightweight & Powerful
100% Free with Ollama | No API Keys Required
"""
import asyncio
import json
import os
import sys
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
sys.path.append('src')

from agent.browser_use.browser_use_agent import BrowserUseAgent
from browser.custom_browser import CustomBrowser
from controller.custom_controller import CustomController
from utils import llm_provider

class JobApplier:
    def __init__(self):
        self.config = self.load_config()
        self.llm = None
        self.browser = None
        self.controller = None
        
    def load_config(self):
        """Load or create job configuration"""
        config_file = "job_config.json"
        default_config = {
            "personal_info": {
                "name": "Your Name",
                "email": "your.email@example.com",
                "phone": "(555) 123-4567",
                "linkedin": "linkedin.com/in/yourprofile"
            },
            "job_preferences": {
                "positions": ["Software Engineer", "Python Developer", "Full Stack Developer"],
                "locations": ["Remote", "New York", "San Francisco"],
                "experience_levels": ["Entry Level", "Mid Level"],
                "job_types": ["Full-time", "Contract"]
            },
            "application_settings": {
                "max_applications_per_session": 5,
                "preferred_sites": ["LinkedIn", "Indeed", "Glassdoor"],
                "auto_apply_only": True
            }
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"📝 Created {config_file} - Please update with your information!")
            return default_config
    
    def check_ollama(self):
        """Check if Ollama is installed and has models"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                models = result.stdout.strip()
                if 'qwen2.5:7b' in models:
                    return True, "qwen2.5:7b"
                elif 'llama3.1:8b' in models:
                    return True, "llama3.1:8b"
                elif 'llama3.1:70b' in models:
                    return True, "llama3.1:70b"
                elif models and 'NAME' in models:
                    # Get first available model
                    lines = models.split('\n')[1:]  # Skip header
                    if lines:
                        model_name = lines[0].split()[0]
                        return True, model_name
                return False, "No models found"
            return False, "Ollama not responding"
        except FileNotFoundError:
            return False, "Ollama not installed"
    
    async def setup_agent(self, task_description):
        """Initialize the browser automation agent"""
        # Check Ollama
        ollama_ok, model_or_error = self.check_ollama()
        if not ollama_ok:
            raise Exception(f"Ollama issue: {model_or_error}")
        
        print(f"🧠 Using Ollama model: {model_or_error}")
        
        # Initialize LLM
        self.llm = llm_provider.get_llm_model(
            provider="ollama",
            model_name=model_or_error,
            temperature=0.1
        )
        
        # Initialize browser and controller
        self.browser = CustomBrowser()
        self.controller = CustomController()
        
        # Create agent with task
        agent = BrowserUseAgent(
            task=task_description,
            llm=self.llm,
            browser=self.browser,
            controller=self.controller
        )
        
        return agent
    
    def create_job_prompt(self, site="LinkedIn"):
        """Create optimized job application prompt"""
        info = self.config["personal_info"]
        prefs = self.config["job_preferences"]
        settings = self.config["application_settings"]
        
        positions = " OR ".join(prefs["positions"])
        locations = " OR ".join(prefs["locations"])
        
        prompt = f"""
You are an expert job application assistant. Help me apply for jobs on {site}.

PERSONAL INFORMATION:
- Name: {info["name"]}
- Email: {info["email"]}
- Phone: {info["phone"]}
- LinkedIn: {info["linkedin"]}

JOB SEARCH CRITERIA:
- Positions: {positions}
- Locations: {locations}
- Experience: {" OR ".join(prefs["experience_levels"])}
- Type: {" OR ".join(prefs["job_types"])}

INSTRUCTIONS:
1. Go to {site.lower()}.com/jobs
2. Search for positions matching my criteria
3. Filter for:
   - Remote or preferred locations
   - Entry/Mid level experience
   - Easy Apply or Quick Apply options
4. Apply to {settings["max_applications_per_session"]} suitable positions:
   - Read job descriptions carefully
   - Only apply to legitimate {positions} positions
   - Fill application forms with my information above
   - Submit applications
5. Provide detailed summary:
   - Company names and positions applied to
   - Application status for each
   - Any issues encountered

IMPORTANT: Be selective - quality over quantity. Only apply to positions that match my skills and preferences.
"""
        return prompt
    
    async def apply_to_site(self, site):
        """Apply to jobs on a specific site"""
        print(f"\n🚀 Starting {site} Job Applications")
        print("=" * 50)
        
        try:
            # Create job prompt
            prompt = self.create_job_prompt(site)
            
            # Setup agent
            print("🤖 Setting up automation agent...")
            agent = await self.setup_agent(prompt)
            
            print(f"🎯 Applying to {site} jobs...")
            print("📱 Browser window will open - watch the automation!")
            
            # Run automation
            result = await agent.run()
            
            print(f"\n✅ {site} applications completed!")
            return True, result
            
        except Exception as e:
            print(f"❌ Error with {site}: {e}")
            return False, str(e)
    
    async def run_job_hunt(self):
        """Run complete job hunting session"""
        print("🎯 STARTING JOB HUNT SESSION")
        print("=" * 50)
        
        sites = self.config["application_settings"]["preferred_sites"]
        results = {}
        
        for site in sites:
            success, result = await self.apply_to_site(site)
            results[site] = {"success": success, "result": result}
            
            if success:
                print(f"✅ {site}: Success")
            else:
                print(f"❌ {site}: Failed - {result}")
            
            # Small delay between sites
            await asyncio.sleep(2)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"job_applications_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📊 Results saved to: {results_file}")
        return results

def install_ollama_model():
    """Install recommended Ollama model"""
    print("📥 Installing Qwen2.5:7b model...")
    print("This is the best model for job applications (4.7GB)")
    
    try:
        subprocess.run(['ollama', 'pull', 'qwen2.5:7b'], check=True)
        print("✅ Model installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install model")
        return False
    except FileNotFoundError:
        print("❌ Ollama not found. Please install from: https://ollama.com")
        return False

def main():
    """Main application"""
    print("🤖 ULTIMATE JOB APPLIER")
    print("=" * 30)
    print("💰 100% Free | 🔒 Private | ⚡ Fast")
    print()
    
    applier = JobApplier()
    
    # Check Ollama setup
    ollama_ok, model_or_error = applier.check_ollama()
    
    if not ollama_ok:
        print(f"⚠️  Ollama issue: {model_or_error}")
        if "not installed" in model_or_error:
            print("📖 Install Ollama from: https://ollama.com")
            return
        elif "No models" in model_or_error:
            print("💡 Would you like to install the recommended model?")
            choice = input("Install Qwen2.5:7b? (y/n): ").strip().lower()
            if choice == 'y':
                if install_ollama_model():
                    ollama_ok = True
                else:
                    return
            else:
                return
    
    if ollama_ok:
        print("✅ Ollama ready!")
        print(f"🧠 Model: {model_or_error}")
        print()
        
        print("📋 Choose an option:")
        print("1. Quick Apply (LinkedIn only)")
        print("2. Full Job Hunt (All sites)")
        print("3. Edit Configuration")
        print("4. Exit")
        
        while True:
            try:
                choice = input("\n👉 Enter choice (1-4): ").strip()
                
                if choice == "1":
                    print("\n🚀 Quick LinkedIn application...")
                    asyncio.run(applier.apply_to_site("LinkedIn"))
                    break
                elif choice == "2":
                    print("\n🚀 Full job hunt session...")
                    asyncio.run(applier.run_job_hunt())
                    break
                elif choice == "3":
                    print(f"\n📝 Edit job_config.json with your information")
                    print("Then run this script again")
                    break
                elif choice == "4":
                    print("👋 Good luck with your job search!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break

if __name__ == "__main__":
    main()
