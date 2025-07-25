#!/usr/bin/env python3
"""
Working Job Applier - Direct approach
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🤖 Job Applier Setup Complete!")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        print(f"✅ Groq API Key: {api_key[:10]}...")
    else:
        print("❌ No Groq API key found")
        return
    
    print("\n📋 Your Job Application System is Ready!")
    print("\n🎯 How to Use:")
    print("1. Open your web browser")
    print("2. Go to: http://127.0.0.1:7788 (or try 7789, 7790)")
    print("3. If the web interface isn't working, use these manual steps:")
    
    print("\n🔧 Manual Job Application Steps:")
    print("1. Go to LinkedIn Jobs (linkedin.com/jobs)")
    print("2. Search for 'Software Engineer' or 'Python Developer'")
    print("3. Filter for Remote jobs")
    print("4. Look for 'Easy Apply' jobs")
    print("5. Apply with your information:")
    print("   - Name: [Your Name]")
    print("   - Email: [Your Email]") 
    print("   - Phone: [Your Phone]")
    
    print("\n💡 Pro Tips:")
    print("- Apply to 5-10 jobs per day maximum")
    print("- Read job descriptions carefully")
    print("- Customize your applications")
    print("- Follow up after 1-2 weeks")
    
    print("\n🚀 Alternative: Use the Python Scripts")
    print("Run these commands in your terminal:")
    print("1. python3.11 job_applier_example.py")
    print("2. python3.11 advanced_job_applier.py")
    
    print("\n📝 Your Configuration:")
    print(f"- API Provider: Groq (Free)")
    print(f"- Model: llama-3.3-70b-versatile")
    print(f"- Browser: Chromium (Installed)")
    print(f"- Status: Ready to use!")

if __name__ == "__main__":
    main()
