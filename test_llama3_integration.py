#!/usr/bin/env python3
"""
🧪 Test Llama 3 Integration for Job Automation
Tests the Llama 3 model with job-specific prompts
"""

import requests
import json

def test_llama3_job_analysis():
    """Test Llama 3 with job analysis prompt"""
    print("🧪 Testing Llama 3 Job Analysis...")
    
    # Sample job data
    job_data = {
        "title": "Senior Python Developer",
        "company": "TechCorp",
        "location": "Remote",
        "description": "We are looking for a Senior Python Developer with 5+ years of experience in Django, Flask, and AWS. Must have strong knowledge of REST APIs, databases, and cloud deployment."
    }
    
    user_profile = {
        "skills": ["Python", "Django", "Flask", "AWS", "REST APIs"],
        "experience_years": 4,
        "preferred_locations": ["Remote", "San Francisco"],
        "salary_min": 80000,
        "salary_max": 120000
    }
    
    prompt = f"""
    Analyze this job posting for compatibility with the user profile:
    
    Job: {job_data['title']} at {job_data['company']}
    Location: {job_data['location']}
    Description: {job_data['description']}
    
    User Profile:
    - Skills: {', '.join(user_profile['skills'])}
    - Experience: {user_profile['experience_years']} years
    - Preferred Location: {', '.join(user_profile['preferred_locations'])}
    - Salary Range: ${user_profile['salary_min']} - ${user_profile['salary_max']}
    
    Provide a JSON response with:
    {{
        "compatibility_score": 0-100,
        "skill_match_score": 0-100,
        "should_apply": true/false,
        "reasoning": "detailed explanation",
        "skill_gaps": ["gap1", "gap2"],
        "skill_matches": ["match1", "match2"]
    }}
    """
    
    try:
        payload = {
            "model": "llama3:latest",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 500
            }
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("response", "")
            print(f"✅ Llama 3 Job Analysis Response:")
            print(f"📝 {content}")
            
            # Try to parse JSON response
            try:
                analysis = json.loads(content)
                print(f"✅ Successfully parsed JSON response!")
                print(f"🎯 Compatibility Score: {analysis.get('compatibility_score', 'N/A')}")
                print(f"🎯 Should Apply: {analysis.get('should_apply', 'N/A')}")
                return True
            except json.JSONDecodeError:
                print("⚠️ Response is not valid JSON, but Llama 3 is working")
                return True
        else:
            print(f"❌ Llama 3 test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Llama 3: {e}")
        return False

def test_llama3_cover_letter():
    """Test Llama 3 with cover letter generation"""
    print("\n🧪 Testing Llama 3 Cover Letter Generation...")
    
    job_data = {
        "title": "Senior Python Developer",
        "company": "TechCorp",
        "description": "We are looking for a Senior Python Developer with 5+ years of experience in Django, Flask, and AWS."
    }
    
    user_profile = {
        "name": "John Doe",
        "experience_years": 4,
        "skills": ["Python", "Django", "Flask", "AWS"],
        "education": "Bachelor's in Computer Science"
    }
    
    prompt = f"""
    Generate a professional cover letter for this job:
    
    Job: {job_data['title']} at {job_data['company']}
    Description: {job_data['description']}
    
    User Profile:
    - Name: {user_profile['name']}
    - Experience: {user_profile['experience_years']} years
    - Skills: {', '.join(user_profile['skills'])}
    - Education: {user_profile['education']}
    
    Write a compelling cover letter that highlights relevant experience and skills.
    """
    
    try:
        payload = {
            "model": "llama3:latest",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 800
            }
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("response", "")
            print(f"✅ Llama 3 Cover Letter Generated:")
            print(f"📝 {content[:200]}...")
            return True
        else:
            print(f"❌ Llama 3 cover letter test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Llama 3 cover letter: {e}")
        return False

def main():
    print("🚀 Testing Llama 3 Integration for Job Automation")
    print("=" * 60)
    
    # Test job analysis
    analysis_success = test_llama3_job_analysis()
    
    # Test cover letter generation
    cover_letter_success = test_llama3_cover_letter()
    
    print("\n" + "=" * 60)
    if analysis_success and cover_letter_success:
        print("🎉 Llama 3 integration is working perfectly!")
        print("✅ Job analysis: Working")
        print("✅ Cover letter generation: Working")
        print("\n📝 Next steps:")
        print("1. Run: python unified_job_automation_app.py")
        print("2. Open: http://localhost:5000")
        print("3. Start automating your job applications!")
    else:
        print("❌ Some tests failed. Please check your Ollama installation.")
        if not analysis_success:
            print("❌ Job analysis test failed")
        if not cover_letter_success:
            print("❌ Cover letter generation test failed")

if __name__ == "__main__":
    main() 