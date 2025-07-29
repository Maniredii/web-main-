"""
Test script for resume optimization functionality
"""

import os
import logging
from resume_optimizer import ResumeOptimizer
from job_description_parser import JobDescriptionParser
from resume_parser import ResumeParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_resume_parsing():
    """Test resume parsing functionality"""
    print("🔍 Testing Resume Parsing...")
    
    resume_path = "sample resume.docx"
    if not os.path.exists(resume_path):
        print(f"❌ Resume file not found: {resume_path}")
        return False
    
    parser = ResumeParser()
    resume_content = parser.parse_resume(resume_path)
    
    if resume_content:
        print(f"✅ Resume parsed successfully!")
        print(f"   Name: {resume_content.name}")
        print(f"   Email: {resume_content.email}")
        print(f"   Technical Skills: {len(resume_content.technical_skills)} found")
        print(f"   Programming Languages: {resume_content.programming_languages}")
        print(f"   ATS Score: {resume_content.ats_score:.2f}/100")
        print(f"   Word Count: {resume_content.word_count}")
        return True
    else:
        print("❌ Failed to parse resume")
        return False

def test_job_description_parsing():
    """Test job description parsing functionality"""
    print("\n🔍 Testing Job Description Parsing...")
    
    sample_job_description = """
    Software Engineer - Python Developer
    
    We are looking for a skilled Python Developer to join our team.
    
    Requirements:
    - 3+ years of experience in Python development
    - Strong knowledge of Django and Flask frameworks
    - Experience with PostgreSQL and Redis
    - Familiarity with AWS cloud services
    - Bachelor's degree in Computer Science or related field
    
    Preferred:
    - Experience with React.js
    - Knowledge of Docker and Kubernetes
    - Agile development experience
    
    Responsibilities:
    - Develop and maintain web applications
    - Collaborate with cross-functional teams
    - Write clean, maintainable code
    - Participate in code reviews
    """
    
    parser = JobDescriptionParser()
    requirements = parser.parse_job_description(
        sample_job_description,
        job_title="Software Engineer - Python Developer",
        company="Tech Company"
    )
    
    print(f"✅ Job description parsed successfully!")
    print(f"   Programming Languages: {requirements.programming_languages}")
    print(f"   Frameworks/Tools: {requirements.frameworks_tools}")
    print(f"   Required Skills: {requirements.required_skills}")
    print(f"   ATS Keywords: {len(requirements.ats_keywords)} found")
    print(f"   Experience Level: {requirements.experience_level}")
    
    return requirements

def test_resume_optimization():
    """Test complete resume optimization workflow"""
    print("\n🔧 Testing Resume Optimization...")
    
    resume_path = "sample resume.docx"
    if not os.path.exists(resume_path):
        print(f"❌ Resume file not found: {resume_path}")
        return False
    
    sample_job_description = """
    Senior Python Developer Position
    
    We are seeking an experienced Python developer to join our growing team.
    
    Required Skills:
    - 5+ years of Python development experience
    - Expertise in Django, Flask, and FastAPI
    - Strong knowledge of PostgreSQL, MongoDB, and Redis
    - Experience with AWS, Docker, and Kubernetes
    - Proficiency in React.js and JavaScript
    - Git version control and CI/CD pipelines
    
    Preferred Qualifications:
    - Machine Learning experience with TensorFlow or PyTorch
    - Experience with microservices architecture
    - Knowledge of GraphQL and REST APIs
    - Agile/Scrum methodology experience
    
    Responsibilities:
    - Design and develop scalable web applications
    - Lead technical discussions and code reviews
    - Mentor junior developers
    - Collaborate with product and design teams
    - Implement best practices for code quality and testing
    """
    
    optimizer = ResumeOptimizer()
    result = optimizer.optimize_resume_for_job(
        resume_path,
        sample_job_description,
        "Senior Python Developer",
        "Tech Innovations Inc"
    )
    
    if result:
        print(f"✅ Resume optimization completed!")
        print(f"   Optimization Score: {result.optimization_score:.2f}/100")
        print(f"   Keyword Matches: {len(result.keyword_matches)}")
        print(f"   Improvements Made: {len(result.improvements_made)}")
        print(f"   Output File: {result.output_file_path}")
        
        if result.improvements_made:
            print("   Specific Improvements:")
            for improvement in result.improvements_made:
                print(f"     • {improvement}")
        
        if result.keyword_matches:
            print("   Top Keyword Matches:")
            sorted_keywords = sorted(result.keyword_matches.items(), 
                                   key=lambda x: x[1], reverse=True)
            for keyword, count in sorted_keywords[:10]:
                print(f"     • {keyword}: {count} times")
        
        return True
    else:
        print("❌ Resume optimization failed")
        return False

def test_integration_with_linkedin_automation():
    """Test integration with LinkedIn automation system"""
    print("\n🔗 Testing LinkedIn Automation Integration...")
    
    try:
        from linkedin_ollama_automation import LinkedInOllamaAutomation
        
        # Check if resume optimization is available
        automation = LinkedInOllamaAutomation()
        
        if hasattr(automation, 'resume_optimizer') and automation.resume_optimizer:
            print("✅ Resume optimization integrated successfully!")
            print(f"   Original Resume Path: {automation.original_resume_path}")
            print(f"   Optimization Enabled: {automation.enable_resume_optimization}")
            return True
        else:
            print("⚠️ Resume optimization not enabled in automation")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Resume Optimization System Tests")
    print("=" * 50)
    
    tests = [
        ("Resume Parsing", test_resume_parsing),
        ("Job Description Parsing", test_job_description_parsing),
        ("Resume Optimization", test_resume_optimization),
        ("LinkedIn Integration", test_integration_with_linkedin_automation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Resume optimization system is ready.")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main()
