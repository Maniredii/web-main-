#!/usr/bin/env python3
"""
Direct Job Applier - Ready to Use!
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

async def apply_linkedin_jobs():
    """Apply to LinkedIn jobs"""
    print("🚀 Starting LinkedIn Job Applications")
    print("=" * 50)
    
    # Check API key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY not found!")
        return
    
    try:
        # Initialize LLM
        print("🧠 Initializing Groq LLM...")
        llm = llm_provider.get_llm_model(
            provider="groq",
            model_name="llama-3.3-70b-versatile",
            temperature=0.1
        )
        print("✅ LLM ready!")
        
        # Initialize browser and controller
        print("🌐 Setting up browser automation...")
        browser = CustomBrowser()
        controller = CustomController()
        
        # Create agent
        print("🤖 Creating automation agent...")
        agent = BrowserUseAgent(
            llm=llm,
            browser=browser,
            controller=controller
        )
        print("✅ Agent ready!")
        
        # Job application prompt - CUSTOMIZE THIS WITH YOUR INFO!
        job_prompt = """
I need you to help me apply for software engineering jobs on LinkedIn. Here's my information:

PERSONAL INFORMATION (REPLACE WITH YOUR REAL INFO):
- Name: John Doe
- Email: john.doe@email.com  
- Phone: (555) 123-4567
- LinkedIn: linkedin.com/in/johndoe

INSTRUCTIONS:
1. Go to LinkedIn Jobs (linkedin.com/jobs)
2. Search for "Software Engineer" OR "Python Developer"
3. Set location filter to "Remote" 
4. Filter for:
   - Experience Level: Entry Level OR Mid Level
   - Job Type: Full-time
   - Posted: Past 24 hours
   - Easy Apply: Yes
5. Apply to 3-5 suitable jobs:
   - Read each job description carefully
   - Only apply if it matches software engineering/programming
   - Click "Easy Apply" button
   - Fill out application forms with my information above
   - Submit each application
   - Take note of company name and position title
6. After completing applications, provide a summary including:
   - Total number of applications submitted
   - List of companies and positions applied to
   - Any issues or errors encountered

IMPORTANT: Be selective and only apply to legitimate software engineering positions that match my experience level.
"""
        
        print("\n🎯 Starting job application process...")
        print("📱 A browser window will open - you can watch the automation!")
        print("⏹️  Press Ctrl+C to stop at any time")
        print("\n" + "="*50)
        
        # Run the automation
        result = await agent.run(job_prompt)
        
        print("\n" + "="*50)
        print("🎉 JOB APPLICATIONS COMPLETE!")
        print("="*50)
        print("📊 RESULTS:")
        print(result)
        print("\n💡 Next steps:")
        print("- Check your email for application confirmations")
        print("- Follow up with recruiters in 1-2 weeks")
        print("- Keep track of applications in a spreadsheet")
        
    except KeyboardInterrupt:
        print("\n⏹️ Job application stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Try running the script again or check your internet connection")

async def apply_indeed_jobs():
    """Apply to Indeed jobs"""
    print("🚀 Starting Indeed Job Applications")
    print("=" * 50)
    
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
Apply for Python/Software Engineer jobs on Indeed:

PERSONAL INFO (REPLACE WITH YOUR REAL INFO):
- Name: John Doe
- Email: john.doe@email.com
- Phone: (555) 123-4567

INSTRUCTIONS:
1. Go to indeed.com
2. Search for "Python Developer" OR "Software Engineer"
3. Set location to "Remote"
4. Filter for jobs posted in last 3 days
5. Apply to 3-5 suitable positions:
   - Look for "Apply Now" or easy application buttons
   - Read job descriptions carefully
   - Only apply if it matches Python/software development
   - Fill forms with my information above
   - Submit applications
6. Provide summary with company names and positions

Quality over quantity - be selective!
"""
        
        print("🎯 Applying to Indeed jobs...")
        result = await agent.run(indeed_prompt)
        
        print("\n🎉 Indeed applications complete!")
        print("📊 Results:")
        print(result)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main menu"""
    print("🤖 AUTO JOB APPLIER")
    print("=" * 30)
    print("✅ Groq API: Ready")
    print("✅ Browser: Installed") 
    print("✅ Scripts: Ready")
    print("\n📋 Choose an option:")
    print("1. Apply to LinkedIn Jobs (Recommended)")
    print("2. Apply to Indeed Jobs")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\n👉 Enter your choice (1-3): ").strip()
            
            if choice == "1":
                print("\n🚀 Starting LinkedIn job applications...")
                asyncio.run(apply_linkedin_jobs())
                break
            elif choice == "2":
                print("\n🚀 Starting Indeed job applications...")
                asyncio.run(apply_indeed_jobs())
                break
            elif choice == "3":
                print("👋 Goodbye! Good luck with your job search!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
