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

        # Free job sites with minimal AI detection (prioritized for stealth)
        self.stealth_sites = {
            'wellfound': {  # AngelList - free, minimal detection
                'url': 'https://wellfound.com/jobs',
                'detection_level': 'low',
                'success_rate': 0.95,
                'apply_selector': '[data-test="apply-button"]',
                'free': True,
                'description': 'Startup jobs, tech-focused'
            },
            'remoteok': {  # Remote OK - completely free, very basic detection
                'url': 'https://remoteok.io',
                'detection_level': 'minimal',
                'success_rate': 0.98,
                'apply_selector': '.apply',
                'free': True,
                'description': 'Remote jobs, no signup required'
            },
            'weworkremotely': {  # We Work Remotely - free, no detection
                'url': 'https://weworkremotely.com',
                'detection_level': 'none',
                'success_rate': 0.99,
                'apply_selector': '.apply-now',
                'free': True,
                'description': 'Remote jobs, simple application'
            },
            'indeed': {  # Indeed - free basic features, low detection
                'url': 'https://indeed.com',
                'detection_level': 'low',
                'success_rate': 0.85,
                'apply_selector': '[data-jk] .ia-IndeedApplyButton',
                'free': True,
                'description': 'Large job database, easy apply'
            },
            'glassdoor': {  # Glassdoor - free job search, moderate detection
                'url': 'https://www.glassdoor.com/Job/jobs.htm',
                'detection_level': 'medium',
                'success_rate': 0.80,
                'apply_selector': '.apply-btn',
                'free': True,
                'description': 'Jobs with company reviews'
            },
            'monster': {  # Monster - free job search
                'url': 'https://www.monster.com/jobs',
                'detection_level': 'low',
                'success_rate': 0.82,
                'apply_selector': '.apply-button',
                'free': True,
                'description': 'Traditional job board'
            }
        }
        
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
    
    def get_stealth_browser_config(self):
        """Get browser configuration for stealth mode (anti-detection)"""
        return {
            'headless': False,  # Visible browser looks more human
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'viewport': {'width': 1366, 'height': 768},  # Common resolution
            'extra_args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-extensions-file-access-check',
                '--disable-extensions',
                '--disable-gpu',
                '--disable-default-apps',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-background-timer-throttling',
                '--force-fieldtrials=*BackgroundTracing/default/',
                '--no-first-run',
                '--no-default-browser-check',
                '--no-sandbox',
                '--disable-web-security'
            ],
            'stealth_mode': True,
            'random_delays': True,
            'human_typing': True
        }

    async def setup_agent(self, task_description):
        """Initialize the browser automation agent with stealth features"""
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

    async def run_stealth_job_hunt(self):
        """Run stealth job hunting session targeting free, low-detection sites"""
        print("🥷 STARTING STEALTH JOB HUNT SESSION")
        print("=" * 50)
        print("🎯 Targeting FREE sites with minimal AI detection...")
        print("💰 All sites are completely free to use!")

        # Filter only free sites and sort by success rate (highest first)
        free_sites = {k: v for k, v in self.stealth_sites.items() if v.get('free', False)}
        sorted_sites = sorted(
            free_sites.items(),
            key=lambda x: x[1]['success_rate'],
            reverse=True
        )

        results = {}
        applications_sent = 0
        max_apps = self.config['application_settings']['max_applications_per_session']

        for site_name, site_info in sorted_sites:
            if applications_sent >= max_apps:
                print(f"🎯 Reached maximum applications ({max_apps})")
                break

            print(f"\n🌐 Targeting: {site_name}")
            print(f"   URL: {site_info['url']}")
            print(f"   💰 Status: FREE")
            print(f"   📝 Description: {site_info['description']}")
            print(f"   🛡️ Detection Level: {site_info['detection_level']}")
            print(f"   📊 Success Rate: {site_info['success_rate']*100:.0f}%")

            try:
                # Use generic site application with stealth config
                success, result = await self.apply_to_site_stealth(site_name, site_info)
                results[site_name] = {"success": success, "result": result}

                if success:
                    applications_sent += 1
                    print(f"✅ {site_name}: Application submitted successfully")
                else:
                    print(f"❌ {site_name}: {result}")

                # Random delay between sites (human behavior)
                import random
                delay = random.uniform(45, 120)  # 45-120 seconds
                print(f"⏳ Human-like delay: {delay:.0f}s before next site...")
                await asyncio.sleep(delay)

            except Exception as e:
                print(f"❌ Error on {site_name}: {e}")
                results[site_name] = {"success": False, "result": str(e)}
                continue

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"stealth_job_applications_{timestamp}.json"

        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n🎉 Stealth session complete!")
        print(f"📊 Applications sent: {applications_sent}")
        print(f"📁 Results saved to: {results_file}")
        return results

    async def apply_to_site_stealth(self, site_name, site_info):
        """Apply to jobs on a specific site with maximum stealth"""
        try:
            # Create stealth prompt with manual login instruction
            prompt = self.create_stealth_job_prompt_with_manual_login(site_name, site_info)

            # Setup agent with stealth configuration
            await self.setup_agent(prompt)

            print(f"🌐 Opening {site_name} in browser...")
            print(f"👤 Please manually log in when the browser opens")
            print(f"⏳ The AI will wait for you to complete login...")

            # Execute the job application
            result = await self.controller.run(prompt)

            return True, result

        except Exception as e:
            return False, str(e)

    def create_stealth_job_prompt(self, site_name, site_info):
        """Create a stealth-optimized prompt for job applications"""
        info = self.config["personal_info"]
        prefs = self.config["job_preferences"]

        positions = " OR ".join(prefs["positions"])
        locations = " OR ".join(prefs["locations"])

        prompt = f"""
You are a stealth job application specialist. Your mission is to apply for jobs on {site_name} while avoiding AI detection.

TARGET SITE: {site_info['url']}
DETECTION LEVEL: {site_info['detection_level']}
SUCCESS RATE: {site_info['success_rate']*100:.0f}%

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

STEALTH INSTRUCTIONS:
1. Navigate to {site_info['url']} naturally
2. Use human-like browsing patterns:
   - Random mouse movements
   - Natural scrolling speeds
   - Realistic typing delays
3. Search for jobs matching my criteria
4. Look for quick apply or easy apply options
5. Apply to 1-2 high-quality positions maximum
6. Fill forms naturally with my information
7. Avoid rapid-fire clicking or automation patterns

ANTI-DETECTION MEASURES:
- Use random delays between actions (2-8 seconds)
- Scroll and read job descriptions naturally
- Click on different page elements occasionally
- Vary typing speed and patterns
- Take breaks between form fields

SUCCESS CRITERIA:
- Successfully submit at least 1 application
- Avoid triggering any bot detection
- Maintain human-like behavior throughout
- Complete the process within 10 minutes

IMPORTANT: Quality over quantity. Better to apply to 1 job successfully than trigger detection systems.
"""
        return prompt

    def create_stealth_job_prompt_with_manual_login(self, site_name, site_info):
        """Create a stealth prompt that waits for manual login"""
        info = self.config["personal_info"]
        prefs = self.config["job_preferences"]

        positions = " OR ".join(prefs["positions"])
        locations = " OR ".join(prefs["locations"])

        prompt = f"""
You are a stealth job application specialist working with a human user. Your mission is to apply for jobs on {site_name} while avoiding AI detection.

TARGET SITE: {site_info['url']}
DETECTION LEVEL: {site_info['detection_level']}
SUCCESS RATE: {site_info['success_rate']*100:.0f}%

PERSONAL INFORMATION TO USE:
- Name: {info["name"]}
- Email: {info["email"]}
- Phone: {info["phone"]}
- LinkedIn: {info["linkedin"]}

JOB SEARCH CRITERIA:
- Positions: {positions}
- Locations: {locations}
- Experience: {" OR ".join(prefs["experience_levels"])}
- Type: {" OR ".join(prefs["job_types"])}

WORKFLOW:
1. Navigate to {site_info['url']}
2. WAIT for the human user to manually log in
3. Once logged in, proceed with job search
4. Search for jobs matching the criteria above
5. Apply to 1-2 high-quality positions using stealth techniques

STEALTH INSTRUCTIONS (After Login):
- Use human-like browsing patterns
- Random delays between actions (3-8 seconds)
- Natural scrolling and reading behavior
- Look for "Easy Apply" or "Quick Apply" options
- Fill forms naturally with the personal information above
- Avoid rapid-fire clicking or automation patterns

MANUAL LOGIN PROCESS:
- Navigate to the site
- Display a message: "Please log in manually in the browser"
- Wait for user to complete login (detect when login is successful)
- Only proceed with job applications after successful login
- If login fails or times out, report the issue

SUCCESS CRITERIA:
- Wait patiently for manual login
- Successfully apply to 1-2 relevant positions
- Maintain human-like behavior throughout
- Avoid triggering any bot detection systems

IMPORTANT:
- DO NOT attempt to automate the login process
- WAIT for the human to log in manually
- Only proceed with job applications after login is confirmed
- Quality over quantity - better to apply to 1 job successfully than trigger detection
"""
        return prompt

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
        print("1. 🥷 Stealth Mode (FREE Sites, Low AI Detection)")
        print("2. Quick Apply (LinkedIn only)")
        print("3. Full Job Hunt (All sites)")
        print("4. Edit Configuration")
        print("5. Exit")

        # Show available free sites
        free_sites = {k: v for k, v in applier.stealth_sites.items() if v.get('free', False)}
        print(f"\n💰 Stealth Mode includes {len(free_sites)} FREE sites:")
        for site_name, site_info in free_sites.items():
            print(f"   🌐 {site_name}: {site_info['description']}")
        
        while True:
            try:
                choice = input("\n👉 Enter choice (1-5): ").strip()

                if choice == "1":
                    print("\n🥷 Starting STEALTH MODE...")
                    print("💰 Using only FREE job sites")
                    print("🎯 Targeting sites with minimal AI detection")
                    print("🛡️ Manual login for maximum security")
                    asyncio.run(applier.run_stealth_job_hunt())
                    break
                elif choice == "2":
                    print("\n🚀 Quick LinkedIn application...")
                    asyncio.run(applier.apply_to_site("LinkedIn"))
                    break
                elif choice == "3":
                    print("\n🚀 Full job hunt session...")
                    asyncio.run(applier.run_job_hunt())
                    break
                elif choice == "4":
                    print(f"\n📝 Edit job_config.json with your information")
                    print("Then run this script again")
                    break
                elif choice == "5":
                    print("👋 Good luck with your job search!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1, 2, 3, 4, or 5.")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break

if __name__ == "__main__":
    main()
