#!/usr/bin/env python3
"""
Advanced Auto Job Applier with Smart Filtering and Tracking
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List
sys.path.append('src')

from agent.browser_use.browser_use_agent import BrowserUseAgent
from browser.custom_browser import CustomBrowser
from controller.custom_controller import CustomController
from utils import llm_provider

class SmartJobApplier:
    def __init__(self, config_file="job_config.json"):
        self.config = self.load_config(config_file)
        self.agent = None
        self.applications_log = []
        
    def load_config(self, config_file):
        """Load job application configuration"""
        default_config = {
            "personal_info": {
                "name": "Your Name",
                "email": "your.email@example.com",
                "phone": "(555) 123-4567",
                "linkedin": "https://linkedin.com/in/yourprofile",
                "github": "https://github.com/yourusername",
                "portfolio": "https://yourportfolio.com",
                "resume_path": "resume.pdf",
                "cover_letter_template": "I am excited to apply for the {position} role at {company}..."
            },
            "job_criteria": {
                "required_keywords": ["Python", "Software Engineer"],
                "preferred_keywords": ["Django", "React", "AWS", "Docker"],
                "excluded_keywords": ["Senior", "Lead", "Manager"],
                "locations": ["Remote", "San Francisco", "New York"],
                "salary_min": 80000,
                "experience_years": 3,
                "job_types": ["Full-time"],
                "company_size": ["Startup", "Mid-size", "Large"]
            },
            "application_settings": {
                "max_applications_per_day": 25,
                "max_applications_per_site": 15,
                "apply_to_new_postings_only": True,
                "skip_cover_letter_required": False,
                "auto_answer_questions": True
            },
            "job_sites": {
                "linkedin": {"enabled": True, "priority": 1},
                "indeed": {"enabled": True, "priority": 2},
                "glassdoor": {"enabled": True, "priority": 3},
                "angel": {"enabled": False, "priority": 4}
            }
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Create default config file
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default config file: {config_file}")
            print("Please edit the config file with your information before running.")
            return default_config
    
    async def setup_agent(self, task_description="Apply for jobs"):
        """Initialize the browser automation agent"""
        llm = llm_provider.get_llm_model(
            provider="groq",
            model_name="llama-3.3-70b-versatile",
            temperature=0.0
        )

        browser = CustomBrowser()
        controller = CustomController()

        self.agent = BrowserUseAgent(
            task=task_description,
            llm=llm,
            browser=browser,
            controller=controller
        )
    
    def create_smart_prompt(self, site_name: str) -> str:
        """Create an intelligent prompt for job applications"""
        personal = self.config["personal_info"]
        criteria = self.config["job_criteria"]
        settings = self.config["application_settings"]
        
        prompt = f"""
        You are an expert job application assistant. I need you to intelligently apply to jobs on {site_name}.

        MY PROFILE:
        - Name: {personal['name']}
        - Email: {personal['email']}
        - Phone: {personal['phone']}
        - Experience: {criteria['experience_years']} years
        - LinkedIn: {personal.get('linkedin', 'N/A')}
        - GitHub: {personal.get('github', 'N/A')}

        JOB SEARCH STRATEGY:
        1. Search for positions with these REQUIRED keywords: {', '.join(criteria['required_keywords'])}
        2. PREFER jobs with these keywords: {', '.join(criteria['preferred_keywords'])}
        3. AVOID jobs with these keywords: {', '.join(criteria['excluded_keywords'])}
        4. Target locations: {', '.join(criteria['locations'])}
        5. Minimum salary: ${criteria['salary_min']:,} (if shown)

        INTELLIGENT FILTERING:
        - Only apply to jobs that match at least 70% of my criteria
        - Skip jobs requiring more than {criteria['experience_years'] + 2} years experience
        - Prioritize companies with good ratings (4+ stars if visible)
        - Focus on jobs posted within the last 3 days
        - Skip jobs with excessive requirements or red flags

        APPLICATION PROCESS:
        1. Navigate to {site_name}
        2. Search using my criteria
        3. For each potential job:
           a. Read the full job description
           b. Evaluate if it's a good match (be selective!)
           c. If good match, proceed with application
           d. Fill forms accurately with my information
           e. Upload resume if required
           f. Answer screening questions intelligently
           g. Submit application
           h. Record: Company, Position, Date, Status
        4. Apply to maximum {settings['max_applications_per_site']} jobs
        5. Provide detailed summary with company names and positions

        QUALITY OVER QUANTITY: Be selective and only apply to genuinely suitable positions.
        """
        
        return prompt
    
    async def apply_to_site(self, site_name: str) -> Dict:
        """Apply to jobs on a specific site"""
        if not self.config["job_sites"][site_name]["enabled"]:
            return {"site": site_name, "status": "disabled", "applications": 0}
        
        print(f"\n🔍 Starting job applications on {site_name.upper()}...")
        
        prompt = self.create_smart_prompt(site_name)
        
        try:
            # Create a new agent for each site with the specific prompt as task
            await self.setup_agent(prompt)
            result = await self.agent.run()
            
            # Log the session
            session_log = {
                "site": site_name,
                "timestamp": datetime.now().isoformat(),
                "result": result,
                "status": "completed"
            }
            self.applications_log.append(session_log)
            
            print(f"✅ Completed {site_name} applications")
            return session_log
            
        except Exception as e:
            error_log = {
                "site": site_name,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error"
            }
            self.applications_log.append(error_log)
            print(f"❌ Error on {site_name}: {e}")
            return error_log
    
    async def run_daily_job_hunt(self):
        """Run a complete daily job hunting session"""
        print("🚀 Starting Smart Job Application Session")
        print("=" * 50)
        
        await self.setup_agent("Daily job hunt session")
        
        # Get enabled sites sorted by priority
        enabled_sites = [
            (site, config) for site, config in self.config["job_sites"].items()
            if config["enabled"]
        ]
        enabled_sites.sort(key=lambda x: x[1]["priority"])
        
        # Apply to each site
        for site_name, site_config in enabled_sites:
            await self.apply_to_site(site_name)
            
            # Brief pause between sites
            await asyncio.sleep(5)
        
        # Save session log
        self.save_session_log()
        
        # Print summary
        self.print_session_summary()
    
    def save_session_log(self):
        """Save the application session log"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"job_applications_{timestamp}.json"
        
        with open(log_file, 'w') as f:
            json.dump(self.applications_log, f, indent=2)
        
        print(f"📝 Session log saved to: {log_file}")
    
    def print_session_summary(self):
        """Print a summary of the job application session"""
        print("\n" + "=" * 50)
        print("📊 JOB APPLICATION SESSION SUMMARY")
        print("=" * 50)
        
        total_sites = len(self.applications_log)
        successful_sites = len([log for log in self.applications_log if log["status"] == "completed"])
        
        print(f"Sites processed: {total_sites}")
        print(f"Successful sites: {successful_sites}")
        print(f"Failed sites: {total_sites - successful_sites}")
        
        for log in self.applications_log:
            status_emoji = "✅" if log["status"] == "completed" else "❌"
            print(f"{status_emoji} {log['site'].upper()}: {log['status']}")
        
        print("\n💡 Tips for next session:")
        print("- Review and update your job_config.json")
        print("- Check the detailed logs for application results")
        print("- Follow up on applications after 1-2 weeks")

async def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        print("Setting up job application configuration...")
        applier = SmartJobApplier()
        print("Please edit job_config.json with your information and run again.")
        return
    
    # Check for Groq API key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ Please set your GROQ_API_KEY in the .env file first!")
        print("Get your free API key from: https://console.groq.com/")
        sys.exit(1)
    
    # Run the job applier
    applier = SmartJobApplier()
    await applier.run_daily_job_hunt()

if __name__ == "__main__":
    asyncio.run(main())
