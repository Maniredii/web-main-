#!/usr/bin/env python3
"""
Test script for Auto Job Applier components
"""

import sys
import os
from auto_job_applier import OllamaManager, ResumeParser, JobScraper

def test_ollama_manager():
    """Test OllamaManager functionality"""
    print("🧪 Testing OllamaManager...")
    
    manager = OllamaManager()
    print(f"Ollama available: {manager.available}")
    
    if manager.available:
        # Test simple query
        response = manager.query("Hello, how are you?")
        print(f"Query response: {response[:100] if response else 'None'}...")
        
        # Test job analysis
        job_desc = "We are looking for a Python developer with experience in web development."
        resume_text = "I am a Python developer with 3 years of experience in Django and Flask."
        
        analysis = manager.analyze_job_compatibility(job_desc, resume_text)
        print(f"Analysis result: {analysis}")
    else:
        print("⚠️ Ollama not available - skipping tests")

def test_resume_parser():
    """Test ResumeParser functionality"""
    print("\n🧪 Testing ResumeParser...")
    
    parser = ResumeParser()
    print(f"Supported formats: {parser.supported_formats}")
    
    # Test with sample resume if available
    sample_resume = "sample resume.docx"
    if os.path.exists(sample_resume):
        try:
            result = parser.parse_resume(sample_resume)
            print(f"Parsed resume length: {len(result['text'])} characters")
            print(f"Skills found: {result['skills'][:3]}")
        except Exception as e:
            print(f"Error parsing resume: {e}")
    else:
        print("⚠️ Sample resume not found - skipping test")

def test_job_scraper():
    """Test JobScraper functionality"""
    print("\n🧪 Testing JobScraper...")
    
    scraper = JobScraper()
    
    # Test job search
    try:
        jobs = scraper.search_jobs("python developer", "remote", "indeed")
        print(f"Found {len(jobs)} jobs")
        if jobs:
            print(f"First job: {jobs[0]['title']} at {jobs[0]['company']}")
    except Exception as e:
        print(f"Error searching jobs: {e}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Auto Job Applier - Component Tests")
    print("=" * 60)
    
    try:
        test_ollama_manager()
        test_resume_parser()
        test_job_scraper()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 