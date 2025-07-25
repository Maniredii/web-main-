#!/usr/bin/env python3
"""
Auto Job Applier Example
This script demonstrates how to use the browser automation agent for job applications.
"""

import asyncio
import os
import sys
sys.path.append('src')

from agent.browser_use.browser_use_agent import BrowserUseAgent
from browser.custom_browser import CustomBrowser
from controller.custom_controller import CustomController
from utils import llm_provider

# Job application configuration
JOB_CONFIG = {
    "personal_info": {
        "name": "Your Name",
        "email": "your.email@example.com",
        "phone": "(555) 123-4567",
        "linkedin": "https://linkedin.com/in/yourprofile",
        "resume_path": "path/to/your/resume.pdf"
    },
    "job_criteria": {
        "keywords": ["Software Engineer", "Python Developer", "Full Stack Developer"],
        "locations": ["Remote", "San Francisco", "New York"],
        "experience_level": ["Entry level", "Mid level"],
        "job_types": ["Full-time", "Contract"]
    },
    "application_limits": {
        "max_applications_per_day": 20,
        "max_applications_per_site": 10
    }
}

class JobApplier:
    def __init__(self):
        self.agent = None
        self.applications_count = 0
        
    async def setup_agent(self):
        """Initialize the browser automation agent"""
        # Get LLM configuration using Groq (free!)
        llm = llm_provider.get_llm_model(
            provider="groq",
            model_name="llama-3.3-70b-versatile",  # Fast and free model
            temperature=0.0
        )
        
        # Create custom browser and controller
        browser = CustomBrowser()
        controller = CustomController()
        
        # Initialize the agent
        self.agent = BrowserUseAgent(
            llm=llm,
            browser=browser,
            controller=controller
        )
        
    async def apply_to_linkedin_jobs(self):
        """Apply to jobs on LinkedIn"""
        linkedin_prompt = f"""
        I want you to help me apply to jobs on LinkedIn. Here's my information:
        
        Personal Info:
        - Name: {JOB_CONFIG['personal_info']['name']}
        - Email: {JOB_CONFIG['personal_info']['email']}
        - Phone: {JOB_CONFIG['personal_info']['phone']}
        
        Job Search Criteria:
        - Keywords: {', '.join(JOB_CONFIG['job_criteria']['keywords'])}
        - Locations: {', '.join(JOB_CONFIG['job_criteria']['locations'])}
        - Experience: {', '.join(JOB_CONFIG['job_criteria']['experience_level'])}
        
        Please do the following:
        1. Go to linkedin.com/jobs
        2. Search for jobs using my criteria
        3. Filter for "Easy Apply" jobs only
        4. Apply to up to {JOB_CONFIG['application_limits']['max_applications_per_site']} suitable positions
        5. For each application:
           - Read the job description carefully
           - Only apply if it matches my criteria
           - Fill out the application form with my information
           - Upload resume if required (skip if not available)
           - Submit the application
           - Take note of the company and position
        6. Provide a summary of all applications submitted
        
        Important: Be careful and thoughtful about each application. Quality over quantity.
        """
        
        try:
            result = await self.agent.run(linkedin_prompt)
            print("LinkedIn job application results:")
            print(result)
            return result
        except Exception as e:
            print(f"Error applying to LinkedIn jobs: {e}")
            return None
    
    async def apply_to_indeed_jobs(self):
        """Apply to jobs on Indeed"""
        indeed_prompt = f"""
        Now let's apply to jobs on Indeed. Use the same personal information and criteria as before.
        
        Please do the following:
        1. Go to indeed.com
        2. Search for jobs using my criteria: {', '.join(JOB_CONFIG['job_criteria']['keywords'])}
        3. Filter for jobs in: {', '.join(JOB_CONFIG['job_criteria']['locations'])}
        4. Look for jobs with "Apply Now" or easy application process
        5. Apply to up to {JOB_CONFIG['application_limits']['max_applications_per_site']} suitable positions
        6. For each application, fill out forms with my information
        7. Provide a summary of applications submitted
        
        Be selective and only apply to jobs that are a good match.
        """
        
        try:
            result = await self.agent.run(indeed_prompt)
            print("Indeed job application results:")
            print(result)
            return result
        except Exception as e:
            print(f"Error applying to Indeed jobs: {e}")
            return None
    
    async def run_job_application_session(self):
        """Run a complete job application session"""
        print("Starting automated job application session...")
        
        # Setup the agent
        await self.setup_agent()
        
        # Apply to different job sites
        linkedin_results = await self.apply_to_linkedin_jobs()
        indeed_results = await self.apply_to_indeed_jobs()
        
        # Summary
        print("\n" + "="*50)
        print("JOB APPLICATION SESSION COMPLETE")
        print("="*50)
        print("LinkedIn Results:", linkedin_results is not None)
        print("Indeed Results:", indeed_results is not None)
        print("Check the browser automation logs for detailed results.")

async def main():
    """Main function to run the job applier"""
    applier = JobApplier()
    await applier.run_job_application_session()

if __name__ == "__main__":
    # Make sure you have your Groq API key set in the .env file
    if not os.getenv("GROQ_API_KEY"):
        print("Please set your GROQ_API_KEY in the .env file first!")
        print("Get your free API key from: https://console.groq.com/")
        sys.exit(1)
    
    # Run the job applier
    asyncio.run(main())
