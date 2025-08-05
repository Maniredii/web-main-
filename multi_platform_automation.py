#!/usr/bin/env python3
"""
🌐 Multi-Platform Job Automation Manager
Unified automation system for multiple job platforms
"""

import json
import logging
import time
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Import platform adapters
from linkedin_platform.linkedin_automation import LinkedInOllamaAutomation, AutomationStrategy
from indeed_platform.indeed_automation import IndeedAdapter
from glassdoor_platform.glassdoor_automation import GlassdoorAdapter
from advanced_job_analyzer import AdvancedJobAnalyzer, JobAnalysis

logger = logging.getLogger(__name__)

@dataclass
class PlatformConfig:
    """Configuration for each platform"""
    name: str
    enabled: bool
    priority: int
    max_applications: int
    search_keywords: List[str]
    locations: List[str]
    experience_level: str

@dataclass
class AutomationResult:
    """Result of automation run"""
    platform: str
    jobs_found: int
    applications_sent: int
    applications_failed: int
    success_rate: float
    errors: List[str]
    duration: float

class MultiPlatformAutomation:
    """Unified automation manager for multiple job platforms"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.job_analyzer = AdvancedJobAnalyzer()
        self.driver = None
        self.results = []
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def setup_browser(self):
        """Setup browser for automation"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Setup Chrome options with stealth
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Random user agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Apply stealth scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Browser setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {e}")
            return False
    
    def get_platform_configs(self) -> List[PlatformConfig]:
        """Get platform configurations"""
        platforms = []
        
        # LinkedIn
        if self.config.get("job_sites", {}).get("linkedin", {}).get("enabled", False):
            platforms.append(PlatformConfig(
                name="linkedin",
                enabled=True,
                priority=self.config["job_sites"]["linkedin"].get("priority", 1),
                max_applications=self.config["linkedin"]["application_settings"].get("max_applications", 10),
                search_keywords=self.config["linkedin"]["search_criteria"].get("keywords", "Python Developer").split(","),
                locations=self.config["linkedin"]["search_criteria"].get("location", "Remote").split(","),
                experience_level="mid"
            ))
        
        # Indeed
        if self.config.get("job_sites", {}).get("indeed", {}).get("enabled", False):
            platforms.append(PlatformConfig(
                name="indeed",
                enabled=True,
                priority=self.config["job_sites"]["indeed"].get("priority", 2),
                max_applications=10,
                search_keywords=self.config["job_criteria"].get("required_keywords", ["Python"]),
                locations=self.config["job_criteria"].get("locations", ["Remote"]),
                experience_level="mid"
            ))
        
        # Glassdoor
        if self.config.get("job_sites", {}).get("glassdoor", {}).get("enabled", False):
            platforms.append(PlatformConfig(
                name="glassdoor",
                enabled=True,
                priority=self.config["job_sites"]["glassdoor"].get("priority", 3),
                max_applications=10,
                search_keywords=self.config["job_criteria"].get("required_keywords", ["Python"]),
                locations=self.config["job_criteria"].get("locations", ["Remote"]),
                experience_level="mid"
            ))
        
        # Sort by priority
        platforms.sort(key=lambda x: x.priority)
        return platforms
    
    def run_automation(self):
        """Run automation across all platforms"""
        logger.info("🚀 Starting Multi-Platform Job Automation")
        
        if not self.setup_browser():
            logger.error("❌ Failed to setup browser")
            return
        
        try:
            # Load user profile
            user_profile = self.load_user_profile()
            if not user_profile:
                logger.error("❌ Failed to load user profile")
                return
            
            # Get platform configurations
            platforms = self.get_platform_configs()
            if not platforms:
                logger.warning("⚠️ No platforms enabled")
                return
            
            logger.info(f"📋 Running automation on {len(platforms)} platforms")
            
            # Run automation for each platform
            for platform_config in platforms:
                if platform_config.enabled:
                    result = self.run_platform_automation(platform_config, user_profile)
                    self.results.append(result)
                    
                    # Add delay between platforms
                    time.sleep(random.uniform(30, 60))
            
            # Generate summary report
            self.generate_summary_report()
            
        except Exception as e:
            logger.error(f"❌ Automation failed: {e}")
        finally:
            self.cleanup()
    
    def run_platform_automation(self, platform_config: PlatformConfig, user_profile: Dict[str, Any]) -> AutomationResult:
        """Run automation for a specific platform"""
        start_time = time.time()
        logger.info(f"🎯 Running automation on {platform_config.name}")
        
        jobs_found = 0
        applications_sent = 0
        applications_failed = 0
        errors = []
        
        try:
            if platform_config.name == "linkedin":
                result = self.run_linkedin_automation(platform_config, user_profile)
            elif platform_config.name == "indeed":
                result = self.run_indeed_automation(platform_config, user_profile)
            elif platform_config.name == "glassdoor":
                result = self.run_glassdoor_automation(platform_config, user_profile)
            else:
                logger.warning(f"⚠️ Unknown platform: {platform_config.name}")
                return AutomationResult(
                    platform=platform_config.name,
                    jobs_found=0,
                    applications_sent=0,
                    applications_failed=0,
                    success_rate=0.0,
                    errors=["Unknown platform"],
                    duration=0.0
                )
            
            # Extract results
            jobs_found = result.get("jobs_found", 0)
            applications_sent = result.get("applications_sent", 0)
            applications_failed = result.get("applications_failed", 0)
            errors = result.get("errors", [])
            
        except Exception as e:
            logger.error(f"❌ {platform_config.name} automation failed: {e}")
            errors.append(str(e))
        
        duration = time.time() - start_time
        success_rate = (applications_sent / (applications_sent + applications_failed) * 100) if (applications_sent + applications_failed) > 0 else 0
        
        return AutomationResult(
            platform=platform_config.name,
            jobs_found=jobs_found,
            applications_sent=applications_sent,
            applications_failed=applications_failed,
            success_rate=success_rate,
            errors=errors,
            duration=duration
        )
    
    def run_linkedin_automation(self, platform_config: PlatformConfig, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Run LinkedIn automation"""
        try:
            # Create LinkedIn automation instance
            automation = LinkedInOllamaAutomation(
                profile_path="my_details.json",
                strategy=AutomationStrategy.CONSERVATIVE
            )
            
            # Set the driver
            automation.driver = self.driver
            
            # Run LinkedIn automation
            automation.run_automation()
            
            return {
                "jobs_found": len(automation.jobs_found) if hasattr(automation, 'jobs_found') else 0,
                "applications_sent": automation.applications_sent if hasattr(automation, 'applications_sent') else 0,
                "applications_failed": 0,
                "errors": []
            }
            
        except Exception as e:
            logger.error(f"LinkedIn automation error: {e}")
            return {
                "jobs_found": 0,
                "applications_sent": 0,
                "applications_failed": 0,
                "errors": [str(e)]
            }
    
    def run_indeed_automation(self, platform_config: PlatformConfig, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Run Indeed automation"""
        try:
            adapter = IndeedAdapter(self.driver, user_profile)
            
            jobs_found = 0
            applications_sent = 0
            applications_failed = 0
            
            # Search for jobs on each keyword/location combination
            for keyword in platform_config.search_keywords:
                for location in platform_config.locations:
                    jobs = adapter.search_jobs(keyword, location, platform_config.experience_level)
                    jobs_found += len(jobs)
                    
                    # Apply to jobs
                    for job in jobs[:platform_config.max_applications]:
                        result = adapter.apply_to_job(job)
                        if result["success"]:
                            applications_sent += 1
                        else:
                            applications_failed += 1
                        
                        # Add delay between applications
                        time.sleep(random.uniform(30, 60))
            
            return {
                "jobs_found": jobs_found,
                "applications_sent": applications_sent,
                "applications_failed": applications_failed,
                "errors": []
            }
            
        except Exception as e:
            logger.error(f"Indeed automation error: {e}")
            return {
                "jobs_found": 0,
                "applications_sent": 0,
                "applications_failed": 0,
                "errors": [str(e)]
            }
    
    def run_glassdoor_automation(self, platform_config: PlatformConfig, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Run Glassdoor automation"""
        try:
            adapter = GlassdoorAdapter(self.driver, user_profile)
            
            jobs_found = 0
            applications_sent = 0
            applications_failed = 0
            
            # Search for jobs on each keyword/location combination
            for keyword in platform_config.search_keywords:
                for location in platform_config.locations:
                    jobs = adapter.search_jobs(keyword, location, platform_config.experience_level)
                    jobs_found += len(jobs)
                    
                    # Apply to jobs
                    for job in jobs[:platform_config.max_applications]:
                        result = adapter.apply_to_job(job)
                        if result["success"]:
                            applications_sent += 1
                        else:
                            applications_failed += 1
                        
                        # Add delay between applications
                        time.sleep(random.uniform(30, 60))
            
            return {
                "jobs_found": jobs_found,
                "applications_sent": applications_sent,
                "applications_failed": applications_failed,
                "errors": []
            }
            
        except Exception as e:
            logger.error(f"Glassdoor automation error: {e}")
            return {
                "jobs_found": 0,
                "applications_sent": 0,
                "applications_failed": 0,
                "errors": [str(e)]
            }
    
    def load_user_profile(self) -> Optional[Dict[str, Any]]:
        """Load user profile from my_details.json"""
        try:
            with open("my_details.json", 'r') as f:
                data = json.load(f)
                
            # Convert to unified format
            profile = {
                "name": data.get("personal_info", {}).get("name", ""),
                "email": data.get("personal_info", {}).get("email", ""),
                "phone": data.get("personal_info", {}).get("phone", ""),
                "location": data.get("personal_info", {}).get("location", ""),
                "current_title": data.get("professional_info", {}).get("current_title", ""),
                "experience_years": data.get("professional_info", {}).get("experience_years", 0),
                "skills": data.get("professional_info", {}).get("skills", []),
                "education": data.get("professional_info", {}).get("education", ""),
                "resume_path": data.get("documents", {}).get("resume_path", "")
            }
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to load user profile: {e}")
            return None
    
    def generate_summary_report(self):
        """Generate summary report of all automation runs"""
        logger.info("📊 Generating Summary Report")
        
        total_jobs_found = sum(r.jobs_found for r in self.results)
        total_applications_sent = sum(r.applications_sent for r in self.results)
        total_applications_failed = sum(r.applications_failed for r in self.results)
        total_duration = sum(r.duration for r in self.results)
        
        overall_success_rate = (total_applications_sent / (total_applications_sent + total_applications_failed) * 100) if (total_applications_sent + total_applications_failed) > 0 else 0
        
        print("\n" + "="*60)
        print("🎯 MULTI-PLATFORM AUTOMATION SUMMARY")
        print("="*60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Total Duration: {total_duration/60:.1f} minutes")
        print(f"🔍 Total Jobs Found: {total_jobs_found}")
        print(f"📝 Total Applications Sent: {total_applications_sent}")
        print(f"❌ Total Applications Failed: {total_applications_failed}")
        print(f"📈 Overall Success Rate: {overall_success_rate:.1f}%")
        print("\n📊 Platform Breakdown:")
        
        for result in self.results:
            print(f"  {result.platform.upper()}:")
            print(f"    Jobs Found: {result.jobs_found}")
            print(f"    Applications: {result.applications_sent} sent, {result.applications_failed} failed")
            print(f"    Success Rate: {result.success_rate:.1f}%")
            print(f"    Duration: {result.duration/60:.1f} minutes")
            if result.errors:
                print(f"    Errors: {', '.join(result.errors)}")
            print()
        
        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_jobs_found": total_jobs_found,
                "total_applications_sent": total_applications_sent,
                "total_applications_failed": total_applications_failed,
                "overall_success_rate": overall_success_rate,
                "total_duration": total_duration
            },
            "platform_results": [
                {
                    "platform": r.platform,
                    "jobs_found": r.jobs_found,
                    "applications_sent": r.applications_sent,
                    "applications_failed": r.applications_failed,
                    "success_rate": r.success_rate,
                    "duration": r.duration,
                    "errors": r.errors
                }
                for r in self.results
            ]
        }
        
        filename = f"multi_platform_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📄 Detailed report saved to: {filename}")
        print("="*60)
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🧹 Browser cleanup complete")
            except Exception as e:
                logger.error(f"Failed to cleanup browser: {e}")

def main():
    """Main function to run multi-platform automation"""
    print("🌐 Multi-Platform Job Automation")
    print("="*50)
    print("🛡️  Enhanced security features enabled")
    print("🤖 AI-powered job analysis")
    print("📊 Real-time monitoring")
    print("="*50)
    
    # Create and run automation
    automation = MultiPlatformAutomation()
    automation.run_automation()

if __name__ == "__main__":
    main() 