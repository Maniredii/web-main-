#!/usr/bin/env python3
"""
Simple Job Applier using Groq API
Run this directly without the web interface
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.append('src')

from agent.browser_use.browser_use_agent import BrowserUseAgent
from browser.custom_browser import CustomBrowser
from controller.custom_controller import CustomController
from utils import llm_provider

async def apply_for_jobs():
    """Simple job application function"""
    
    print("🚀 Starting Simple Job Applier with Groq")
    print("=" * 50)
    
    # Check API key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY not found!")
        print("Please set your Groq API key in the .env file")
        return
    
    try:
        # Initialize LLM with Groq
        print("🧠 Initializing Groq LLM...")
        llm = llm_provider.get_llm_model(
            provider="groq",
            model_name="llama-3.3-70b-versatile",
            temperature=0.1
        )
        print("✅ LLM initialized successfully")
        
        # Initialize browser and controller
        print("🌐 Setting up browser...")
        browser = CustomBrowser()
        controller = CustomController()
        
        # Job application prompt
        job_prompt = """
I need you to help me apply for software engineering jobs. Here's what I want you to do:

Personal Information to use:
- Name: John Doe (replace with your actual name)
- Email: john.doe@email.com (replace with your actual email)
- Phone: (555) 123-4567 (replace with your actual phone)

Instructions:
1. Go to LinkedIn Jobs (linkedin.com/jobs)
2. Search for "Software Engineer" jobs
3. Filter for:
   - Location: Remote
   - Experience Level: Entry Level or Mid Level
   - Job Type: Full-time
   - Posted: Past 24 hours
4. Look for jobs with "Easy Apply" button
5. For each suitable job (apply to maximum 3 jobs):
   - Read the job description carefully
   - Only apply if it matches software engineering/programming
   - Click "Easy Apply"
   - Fill out the application form with my information above
   - Submit the application
   - Take note of the company name and position
6. After applying, provide a summary of:
   - How many jobs you applied to
   - Company names and positions
   - Any issues encountered

Important: Be selective and only apply to legitimate software engineering positions.
"""
        
        print("\n🎯 Starting job application process...")
        print("This will open a browser window - you can watch the automation in action!")
        print("Press Ctrl+C to stop at any time.")

        # Initialize agent with the job prompt as task
        print("🤖 Creating browser automation agent...")
        agent = BrowserUseAgent(
            task=job_prompt,
            llm=llm,
            browser=browser,
            controller=controller
        )
        print("✅ Agent ready!")

        # Run the agent
        result = await agent.run()
        
        print("\n" + "=" * 50)
        print("🎉 JOB APPLICATION COMPLETE!")
        print("=" * 50)
        print("Results:")
        print(result)
        
    except KeyboardInterrupt:
        print("\n⏹️ Job application stopped by user")
    except Exception as e:
        print(f"\n❌ Error during job application: {e}")
        print("Please check your internet connection and API key")

async def apply_to_indeed():
    """Apply to jobs on Indeed"""
    
    print("🚀 Starting Indeed Job Applications")
    print("=" * 50)
    
    # Check API key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY not found!")
        return
    
    try:
        # Initialize everything
        llm = llm_provider.get_llm_model(
            provider="groq",
            model_name="llama-3.3-70b-versatile",
            temperature=0.1
        )
        
        browser = CustomBrowser()
        controller = CustomController()
        agent = BrowserUseAgent(llm=llm, browser=browser, controller=controller)
        
        indeed_prompt = """
Go to Indeed.com and apply for Python developer jobs:

Personal Info:
- Name: John Doe (use your real name)
- Email: john.doe@email.com (use your real email)
- Phone: (555) 123-4567 (use your real phone)

Instructions:
1. Go to indeed.com
2. Search for "Python Developer" or "Software Engineer"
3. Set location to "Remote" 
4. Filter for jobs posted in the last 3 days
5. Look for jobs with "Apply Now" or easy application
6. Apply to 3-5 suitable positions:
   - Read job description
   - Only apply if it matches Python/software development
   - Fill forms with my information
   - Submit applications
7. Provide summary with company names and positions applied to

Be selective - quality over quantity!
"""
        
        print("🎯 Applying to Indeed jobs...")
        result = await agent.run(indeed_prompt)
        
        print("\n🎉 Indeed applications complete!")
        print(result)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function with menu"""
    print("🤖 Simple Job Applier")
    print("=" * 30)
    print("1. Apply to LinkedIn Jobs")
    print("2. Apply to Indeed Jobs") 
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(apply_for_jobs())
    elif choice == "2":
        asyncio.run(apply_to_indeed())
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
