#!/usr/bin/env python3
"""
🔧 Create Sample Profile
Creates a sample user profile to demonstrate the profile management system
"""

from profile_manager import (
    UserProfile, PersonalInfo, ProfessionalInfo, 
    SearchCriteria, DocumentPaths, ProfileStorage
)

def create_sample_profile():
    """Create a sample profile for demonstration"""
    
    # Create profile instance
    profile = UserProfile()
    
    # Personal Information
    profile.personal_info = PersonalInfo(
        name="John Doe",
        email="john.doe@email.com",
        phone="+1-555-123-4567",
        location="San Francisco, CA, USA",
        linkedin_url="https://linkedin.com/in/johndoe",
        website="https://johndoe.dev"
    )
    
    # Professional Information
    profile.professional_info = ProfessionalInfo(
        current_title="Senior Software Engineer",
        experience_years=5,
        skills=[
            "Python", "JavaScript", "React", "Node.js", 
            "AWS", "Docker", "Kubernetes", "PostgreSQL",
            "Machine Learning", "REST APIs", "Git", "Agile"
        ],
        education="Bachelor's in Computer Science",
        desired_salary="$120,000 - $150,000",
        summary="Experienced software engineer with 5+ years developing scalable web applications and cloud solutions. Passionate about clean code, automation, and continuous learning.",
        certifications=["AWS Solutions Architect", "Certified Kubernetes Administrator"]
    )
    
    # Search Criteria
    profile.search_criteria = SearchCriteria(
        keywords=["Software Engineer", "Full Stack Developer", "Backend Engineer", "Python Developer"],
        location="San Francisco Bay Area",
        experience_level="Mid-Senior level",
        remote_preference=True,
        max_applications=20,
        salary_range="$100,000 - $160,000",
        job_types=["Full-time", "Contract"]
    )
    
    # Document Paths (example paths)
    profile.document_paths = DocumentPaths(
        resume_path="./documents/john_doe_resume.pdf",
        cover_letter_path="./documents/john_doe_cover_letter.docx",
        portfolio_path="https://johndoe.dev/portfolio"
    )
    
    return profile

def main():
    """Create and save sample profile"""
    print("🔧 Creating Sample Profile...")
    
    # Create sample profile
    profile = create_sample_profile()
    
    # Save profile
    storage = ProfileStorage()
    
    if storage.save_profile(profile, "sample_profile.json"):
        print("✅ Sample profile created: sample_profile.json")
        
        # Also save as main profile for automation
        if storage.save_profile(profile, "user_profile.json"):
            print("✅ Main profile created: user_profile.json")
            print("\n📋 Profile Summary:")
            print(f"  Name: {profile.personal_info.name}")
            print(f"  Email: {profile.personal_info.email}")
            print(f"  Title: {profile.professional_info.current_title}")
            print(f"  Experience: {profile.professional_info.experience_years} years")
            print(f"  Skills: {len(profile.professional_info.skills)} skills")
            print(f"  Keywords: {len(profile.search_criteria.keywords)} job keywords")
            print(f"  Remote: {'Yes' if profile.search_criteria.remote_preference else 'No'}")
            print(f"  Max Applications: {profile.search_criteria.max_applications}")
            
            print("\n🚀 Ready to use with LinkedIn automation!")
            print("Run: python linkedin_ollama_automation.py")
        else:
            print("❌ Failed to create main profile")
    else:
        print("❌ Failed to create sample profile")

if __name__ == "__main__":
    main()
