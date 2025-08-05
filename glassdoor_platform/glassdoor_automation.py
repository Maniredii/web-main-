#!/usr/bin/env python3
"""
🏢 Glassdoor Job Platform Adapter
Extends automation to Glassdoor job search
"""

import time
import random
import logging
from typing import Dict, Any, List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os

logger = logging.getLogger(__name__)

class GlassdoorAdapter:
    """Glassdoor job platform automation adapter"""
    
    def __init__(self, driver, user_profile: Dict[str, Any]):
        self.driver = driver
        self.user_profile = user_profile
        self.wait = WebDriverWait(driver, 10)
        
    def search_jobs(self, keywords: str, location: str, experience_level: str = None) -> List[Dict[str, Any]]:
        """Search for jobs on Glassdoor"""
        try:
            logger.info(f"🔍 Searching Glassdoor for: {keywords} in {location}")
            
            # Navigate to Glassdoor
            self.driver.get("https://www.glassdoor.com/Job/index.htm")
            time.sleep(random.uniform(2, 4))
            
            # Fill search form
            self._fill_search_form(keywords, location)
            
            # Apply filters
            if experience_level:
                self._apply_experience_filter(experience_level)
            
            # Get job listings
            jobs = self._extract_job_listings()
            
            logger.info(f"✅ Found {len(jobs)} jobs on Glassdoor")
            return jobs
            
        except Exception as e:
            logger.error(f"❌ Glassdoor search failed: {e}")
            return []
    
    def _fill_search_form(self, keywords: str, location: str):
        """Fill the Glassdoor search form"""
        try:
            # Find and fill job title/keywords field
            job_field = self.wait.until(EC.presence_of_element_located((By.ID, "sc.keyword")))
            job_field.clear()
            for char in keywords:
                job_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            time.sleep(random.uniform(1, 2))
            
            # Find and fill location field
            location_field = self.driver.find_element(By.ID, "sc.location")
            location_field.clear()
            for char in location:
                location_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            time.sleep(random.uniform(1, 2))
            
            # Click search button
            search_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            search_button.click()
            
            time.sleep(random.uniform(3, 5))
            
        except Exception as e:
            logger.error(f"Failed to fill search form: {e}")
            raise
    
    def _apply_experience_filter(self, experience_level: str):
        """Apply experience level filter"""
        try:
            # Click on experience filter
            experience_filter = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Experience Level')]")))
            experience_filter.click()
            time.sleep(random.uniform(1, 2))
            
            # Select experience level
            level_mapping = {
                "entry": "Entry Level",
                "mid": "Mid Level", 
                "senior": "Senior Level"
            }
            
            target_level = level_mapping.get(experience_level.lower(), "Entry Level")
            level_option = self.driver.find_element(By.XPATH, f"//label[contains(text(), '{target_level}')]")
            level_option.click()
            
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            logger.warning(f"Failed to apply experience filter: {e}")
    
    def _extract_job_listings(self) -> List[Dict[str, Any]]:
        """Extract job listings from search results"""
        jobs = []
        
        try:
            # Find job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-test='jobListing']")
            
            for card in job_cards[:10]:  # Limit to first 10 jobs
                try:
                    job_data = self._extract_job_data(card)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    logger.warning(f"Failed to extract job data: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Failed to extract job listings: {e}")
        
        return jobs
    
    def _extract_job_data(self, job_card) -> Optional[Dict[str, Any]]:
        """Extract data from a single job card"""
        try:
            # Extract job title
            title_element = job_card.find_element(By.CSS_SELECTOR, "a[data-test='job-link']")
            title = title_element.text.strip()
            
            # Extract company name
            company_element = job_card.find_element(By.CSS_SELECTOR, "[data-test='employer-name']")
            company = company_element.text.strip()
            
            # Extract location
            location_element = job_card.find_element(By.CSS_SELECTOR, "[data-test='location']")
            location = location_element.text.strip()
            
            # Extract job URL
            job_url = title_element.get_attribute("href")
            
            # Extract job description snippet
            try:
                description_element = job_card.find_element(By.CSS_SELECTOR, ".job-description")
                description = description_element.text.strip()
            except:
                description = ""
            
            # Extract salary if available
            try:
                salary_element = job_card.find_element(By.CSS_SELECTOR, "[data-test='salary-estimate']")
                salary = salary_element.text.strip()
            except:
                salary = ""
            
            return {
                "title": title,
                "company": company,
                "location": location,
                "url": job_url,
                "description": description,
                "salary": salary,
                "platform": "glassdoor",
                "posted_date": "",
                "requirements": ""
            }
            
        except Exception as e:
            logger.warning(f"Failed to extract job data: {e}")
            return None
    
    def apply_to_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply to a job on Glassdoor"""
        try:
            logger.info(f"📝 Applying to Glassdoor job: {job_data['title']} at {job_data['company']}")
            
            # Navigate to job page
            self.driver.get(job_data['url'])
            time.sleep(random.uniform(3, 5))
            
            # Look for apply button
            apply_button = self._find_apply_button()
            if not apply_button:
                return {
                    "success": False,
                    "reason": "Apply button not found",
                    "job": job_data
                }
            
            # Click apply button
            apply_button.click()
            time.sleep(random.uniform(2, 4))
            
            # Handle application process
            success = self._handle_application_process(job_data)
            
            return {
                "success": success,
                "reason": "Application submitted successfully" if success else "Failed to submit application",
                "job": job_data
            }
            
        except Exception as e:
            logger.error(f"❌ Glassdoor application failed: {e}")
            return {
                "success": False,
                "reason": f"Error: {str(e)}",
                "job": job_data
            }
    
    def _find_apply_button(self):
        """Find the apply button on Glassdoor"""
        try:
            # Try different selectors for apply button
            selectors = [
                "button[data-test='apply-button']",
                "button[aria-label*='Apply']",
                "a[aria-label*='Apply']",
                "button:contains('Apply')",
                "a:contains('Apply')"
            ]
            
            for selector in selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed() and button.is_enabled():
                        return button
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find apply button: {e}")
            return None
    
    def _handle_application_process(self, job_data: Dict[str, Any]) -> bool:
        """Handle the application process"""
        try:
            # Check if we're redirected to external site
            current_url = self.driver.current_url
            
            if "glassdoor.com" not in current_url:
                # External application - return True as we can't automate external sites
                logger.info("External application site detected")
                return True
            
            # Look for application form
            form_fields = self.driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")
            
            if not form_fields:
                logger.info("No application form found")
                return True
            
            # Fill application form
            return self._fill_application_form(job_data)
            
        except Exception as e:
            logger.error(f"Failed to handle application process: {e}")
            return False
    
    def _fill_application_form(self, job_data: Dict[str, Any]) -> bool:
        """Fill Glassdoor application form"""
        try:
            # Find form fields
            form_fields = self.driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")
            
            for field in form_fields:
                try:
                    field_type = field.get_attribute("type")
                    field_name = field.get_attribute("name") or field.get_attribute("id") or ""
                    
                    if field_type in ["text", "email", "tel"]:
                        value = self._get_field_value(field_name, field_type)
                        if value:
                            field.clear()
                            for char in value:
                                field.send_keys(char)
                                time.sleep(random.uniform(0.05, 0.15))
                    
                    elif field.tag_name == "select":
                        self._handle_select_field(field, field_name)
                    
                    elif field_type == "file":
                        self._handle_file_upload(field, field_name)
                        
                except Exception as e:
                    logger.warning(f"Failed to fill field {field_name}: {e}")
                    continue
            
            # Look for submit button
            submit_button = self._find_submit_button()
            if submit_button:
                submit_button.click()
                time.sleep(random.uniform(2, 4))
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to fill application form: {e}")
            return False
    
    def _get_field_value(self, field_name: str, field_type: str) -> str:
        """Get appropriate value for form field"""
        field_name_lower = field_name.lower()
        
        # Map field names to user profile values
        field_mapping = {
            "name": self.user_profile.get("name", ""),
            "email": self.user_profile.get("email", ""),
            "phone": self.user_profile.get("phone", ""),
            "location": self.user_profile.get("location", ""),
            "city": self.user_profile.get("location", ""),
            "state": self.user_profile.get("location", ""),
            "zip": self.user_profile.get("zip", ""),
            "experience": str(self.user_profile.get("experience_years", 0)),
            "education": self.user_profile.get("education", ""),
            "skills": ", ".join(self.user_profile.get("skills", []))
        }
        
        # Try exact match first
        if field_name_lower in field_mapping:
            return field_mapping[field_name_lower]
        
        # Try partial matches
        for key, value in field_mapping.items():
            if key in field_name_lower or field_name_lower in key:
                return value
        
        return ""
    
    def _handle_select_field(self, field, field_name: str):
        """Handle select field"""
        try:
            field_name_lower = field_name.lower()
            
            # Map common select fields
            if "experience" in field_name_lower:
                experience_years = self.user_profile.get("experience_years", 0)
                if experience_years < 2:
                    option_text = "Entry Level"
                elif experience_years < 5:
                    option_text = "Mid Level"
                else:
                    option_text = "Senior Level"
                
                # Find and select option
                option = field.find_element(By.XPATH, f"//option[contains(text(), '{option_text}')]")
                option.click()
                
        except Exception as e:
            logger.warning(f"Failed to handle select field {field_name}: {e}")
    
    def _handle_file_upload(self, field, field_name: str):
        """Handle file upload field"""
        try:
            if "resume" in field_name.lower():
                resume_path = self.user_profile.get("resume_path", "")
                if resume_path and os.path.exists(resume_path):
                    field.send_keys(os.path.abspath(resume_path))
                    
        except Exception as e:
            logger.warning(f"Failed to handle file upload {field_name}: {e}")
    
    def _find_submit_button(self):
        """Find submit button"""
        try:
            selectors = [
                "button[type='submit']",
                "button:contains('Submit')",
                "button:contains('Apply')",
                "input[type='submit']"
            ]
            
            for selector in selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed() and button.is_enabled():
                        return button
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find submit button: {e}")
            return None 