#!/usr/bin/env python3
"""
🚀 Setup My Details - Interactive Setup for User Details
"""

import json
import os
from user_details_loader import UserDetailsLoader

def interactive_setup():
    """Interactive setup for user details"""
    print("🚀 LinkedIn Automation - Personal Details Setup")
    print("=" * 50)
    print("This will help you set up your personal details for job applications.")
    print("You can always edit the files later to update your information.\n")
    
    # Choose format
    print("📄 Choose your preferred format:")
    print("1. JSON format (structured, good for developers)")
    print("2. Text format (simple, easy to edit)")
    
    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        if choice in ['1', '2']:
            break
        print("Please enter 1 or 2")
    
    use_json = choice == '1'
    filename = 'my_details.json' if use_json else 'my_details.txt'
    
    print(f"\n📝 Setting up {filename}...")
    
    # Check if file exists
    if os.path.exists(filename):
        overwrite = input(f"\n⚠️ {filename} already exists. Overwrite? (y/n): ").lower().startswith('y')
        if not overwrite:
            print("Setup cancelled. You can edit the existing file manually.")
            return
    
    # Collect basic information
    print(f"\n📋 Please provide your information:")
    print("(Required fields are marked with *)")
    
    details = {}
    
    # Personal Information
    print(f"\n--- Personal Information ---")
    details['name'] = input("* Full Name: ").strip()
    details['email'] = input("* Email: ").strip()
    details['phone'] = input("  Phone (e.g., +1-555-123-4567): ").strip()
    details['location'] = input("  Location (e.g., San Francisco, CA, USA): ").strip()
    details['linkedin'] = input("  LinkedIn URL: ").strip()
    details['website'] = input("  Personal Website: ").strip()
    
    # Professional Information
    print(f"\n--- Professional Information ---")
    details['current_title'] = input("  Current Job Title: ").strip()
    
    exp_years = input("  Years of Experience: ").strip()
    try:
        details['experience_years'] = int(exp_years) if exp_years else 0
    except ValueError:
        details['experience_years'] = 0
    
    details['education'] = input("  Education (e.g., BS Computer Science, MIT): ").strip()
    details['summary'] = input("  Professional Summary (2-3 sentences): ").strip()
    
    # Skills
    print(f"\n  Skills (enter one per line, press Enter twice when done):")
    skills = []
    while True:
        skill = input("    Skill: ").strip()
        if not skill:
            break
        skills.append(skill)
    details['skills'] = skills
    
    # Job Preferences
    print(f"\n--- Job Search Preferences ---")
    
    print(f"  Desired Job Titles (enter one per line, press Enter twice when done):")
    desired_roles = []
    while True:
        role = input("    Job Title: ").strip()
        if not role:
            break
        desired_roles.append(role)
    details['desired_roles'] = desired_roles
    
    details['work_type'] = input("  Work Type (Full-time/Part-time/Contract): ").strip() or "Full-time"
    details['remote_preference'] = input("  Remote Preference (Remote/Hybrid/On-site): ").strip() or "Hybrid"
    
    # Application Settings
    print(f"\n--- Application Settings ---")
    max_apps = input("  Max applications per day (default: 10): ").strip()
    try:
        details['max_applications'] = int(max_apps) if max_apps else 10
    except ValueError:
        details['max_applications'] = 10
    
    # Save the file
    if use_json:
        save_json_format(filename, details)
    else:
        save_text_format(filename, details)
    
    print(f"\n✅ Your details have been saved to {filename}")
    print(f"\n📋 Next Steps:")
    print(f"1. Review and edit {filename} if needed")
    print(f"2. Run the LinkedIn automation: python linkedin_ollama_automation.py")
    print(f"3. Your details will be automatically used for job applications")
    
    # Test the loader
    print(f"\n🧪 Testing your configuration...")
    loader = UserDetailsLoader(filename)
    if loader.is_configured():
        print("✅ Configuration test passed!")
        loader.print_summary()
    else:
        print("⚠️ Configuration needs attention. Please check your details.")

def save_json_format(filename: str, details: dict):
    """Save details in JSON format"""
    json_data = {
        "_instructions": {
            "description": "📋 Your Personal Details for Job Applications",
            "how_to_use": [
                "1. Review and update your information below",
                "2. Save this file after making changes", 
                "3. The LinkedIn automation will automatically use these details"
            ],
            "privacy_note": "Keep this file secure - it contains your personal information"
        },
        "personal_info": {
            "name": details['name'],
            "email": details['email'],
            "phone": details['phone'],
            "location": details['location'],
            "linkedin_url": details['linkedin'],
            "website": details['website']
        },
        "professional_info": {
            "current_title": details['current_title'],
            "experience_years": details['experience_years'],
            "education": details['education'],
            "summary": details['summary'],
            "skills": details['skills']
        },
        "job_search_preferences": {
            "desired_roles": details['desired_roles'],
            "work_type": details['work_type'],
            "remote_preference": details['remote_preference']
        },
        "application_settings": {
            "max_applications_per_day": details['max_applications']
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

def save_text_format(filename: str, details: dict):
    """Save details in text format"""
    content = f"""# 📋 MY PERSONAL DETAILS FOR JOB APPLICATIONS
# =====================================================
# 
# INSTRUCTIONS:
# 1. Review and update your information below
# 2. Save this file after making changes
# 3. The LinkedIn automation will automatically use these details
# =====================================================

# ===== PERSONAL INFORMATION =====
FULL_NAME: {details['name']}
EMAIL: {details['email']}
PHONE: {details['phone']}
LOCATION: {details['location']}
LINKEDIN: {details['linkedin']}
WEBSITE: {details['website']}

# ===== PROFESSIONAL INFORMATION =====
CURRENT_JOB_TITLE: {details['current_title']}
YEARS_OF_EXPERIENCE: {details['experience_years']}
EDUCATION: {details['education']}
SUMMARY: {details['summary']}

# SKILLS (one per line)
SKILLS:
{chr(10).join(details['skills'])}

# ===== JOB SEARCH PREFERENCES =====
# DESIRED JOB TITLES (one per line)
DESIRED_ROLES:
{chr(10).join(details['desired_roles'])}

# WORK PREFERENCES
WORK_TYPE: {details['work_type']}
REMOTE_PREFERENCE: {details['remote_preference']}

# ===== APPLICATION SETTINGS =====
MAX_APPLICATIONS_PER_DAY: {details['max_applications']}
EASY_APPLY_ONLY: true
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def check_existing_setup():
    """Check if user already has details configured"""
    print("🔍 Checking for existing configuration...")
    
    files_to_check = ['my_details.json', 'my_details.txt']
    found_files = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            found_files.append(file_path)
    
    if found_files:
        print(f"✅ Found existing configuration files: {', '.join(found_files)}")
        
        # Test the configuration
        loader = UserDetailsLoader()
        if loader.is_configured():
            print("✅ Your details are already configured!")
            loader.print_summary()
            
            update = input("\nWould you like to update your details? (y/n): ").lower().startswith('y')
            if not update:
                print("Setup skipped. Your existing configuration will be used.")
                return False
        else:
            print("⚠️ Configuration file exists but needs to be completed.")
    else:
        print("📝 No existing configuration found. Let's set up your details!")
    
    return True

if __name__ == "__main__":
    try:
        if check_existing_setup():
            interactive_setup()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup error: {str(e)}")
        print("You can manually edit my_details.json or my_details.txt")
