"""
GUI Automation Controller
Integrates the visual interface with LinkedIn automation system
"""

import threading
import queue
import time
from typing import Dict, List, Optional, Callable
import json
import os
from dataclasses import asdict

from linkedin_gui_dashboard import LinkedInGUIDashboard, JobProgress, AutomationStats
from interactive_resume_editor import InteractiveResumeEditor
from linkedin_ollama_automation import LinkedInOllamaAutomation, JobListing, ApplicationResult

class GUIAutomationController:
    """Controller that manages GUI and automation integration"""
    
    def __init__(self):
        # GUI components
        self.dashboard = LinkedInGUIDashboard()
        self.resume_editor = InteractiveResumeEditor(self.dashboard)
        
        # Automation system
        self.automation: Optional[LinkedInOllamaAutomation] = None
        self.automation_thread: Optional[threading.Thread] = None
        
        # Control flags
        self.automation_running = False
        self.automation_paused = False
        self.waiting_for_resume_approval = False
        self.current_resume_data: Dict = {}
        
        # Communication
        self.resume_approval_event = threading.Event()
        self.approved_resume_content = ""
        self.approved_resume_score = 0.0
        
        # Setup callbacks
        self.setup_callbacks()
        
    def setup_callbacks(self):
        """Setup callbacks between GUI components and automation"""
        # Dashboard callbacks
        self.dashboard.on_pause_callback = self.pause_automation
        self.dashboard.on_resume_callback = self.resume_automation
        self.dashboard.on_stop_callback = self.stop_automation
        
        # Resume editor callbacks
        self.resume_editor.on_save_callback = self.on_resume_approved
        self.resume_editor.on_reject_callback = self.on_resume_rejected
        
        # Set resume editor reference in dashboard
        self.dashboard.resume_editor = self.resume_editor
        
    def start_automation_with_gui(self, config_path: str = "config.json"):
        """Start the automation with GUI interface"""
        try:
            # Initialize automation system
            self.automation = LinkedInOllamaAutomation()
            
            # Setup automation callbacks for GUI updates
            self.setup_automation_callbacks()
            
            # Start automation in separate thread
            self.automation_thread = threading.Thread(
                target=self.run_automation_with_gui_updates,
                daemon=True
            )
            
            # Set the thread reference in dashboard
            self.dashboard.automation_thread = self.automation_thread
            
            # Start the automation
            self.automation_thread.start()
            
            # Start GUI
            self.dashboard.run()
            
        except Exception as e:
            self.dashboard.log_message(f"❌ Failed to start automation: {e}", "error")
    
    def setup_automation_callbacks(self):
        """Setup callbacks to capture automation events for GUI updates"""
        if not self.automation:
            return
        
        # Override automation methods to send GUI updates
        original_apply_to_job = self.automation.apply_to_job
        original_analyze_job = self.automation.analyze_job_with_ollama
        
        def gui_apply_to_job(job: JobListing) -> ApplicationResult:
            # Notify GUI of job start
            self.send_progress_update({
                'type': 'job_started',
                'job_title': job.title,
                'company': job.company,
                'url': job.url
            })
            
            # Call original method with GUI integration
            return self.apply_to_job_with_gui(job, original_apply_to_job)
        
        def gui_analyze_job(job: JobListing) -> Dict:
            result = original_analyze_job(job)
            
            # Send analysis results to GUI
            self.send_progress_update({
                'type': 'job_analysis',
                'compatibility_score': result.get('compatibility_score', 0.0),
                'keywords': result.get('extracted_keywords', [])
            })
            
            return result
        
        # Replace methods
        self.automation.apply_to_job = gui_apply_to_job
        self.automation.analyze_job_with_ollama = gui_analyze_job
    
    def apply_to_job_with_gui(self, job: JobListing, original_method: Callable) -> ApplicationResult:
        """Apply to job with GUI integration for resume optimization"""
        try:
            # Check if resume optimization is enabled
            if (hasattr(self.automation, 'enable_resume_optimization') and 
                self.automation.enable_resume_optimization and
                hasattr(self.automation, 'resume_optimizer') and
                self.automation.resume_optimizer):
                
                # Get job description
                job_description = getattr(job, 'description', '')
                
                if job_description and self.automation.original_resume_path:
                    # Start optimization
                    self.send_progress_update({
                        'type': 'optimization_started'
                    })
                    
                    # Perform optimization
                    optimization_result = self.automation.resume_optimizer.optimize_resume_for_job(
                        self.automation.original_resume_path,
                        job_description,
                        job.title,
                        job.company
                    )
                    
                    if optimization_result:
                        # Send optimization complete
                        self.send_progress_update({
                            'type': 'optimization_complete',
                            'optimization_score': optimization_result.optimization_score
                        })
                        
                        # Check if user wants to review resume
                        if self.dashboard.pause_on_optimization_var.get() and not self.dashboard.auto_approve_var.get():
                            # Show resume editor for user review
                            approved_content, approved_score = self.show_resume_editor_and_wait(
                                optimization_result, job, job_description
                            )
                            
                            if approved_content:
                                # Save approved resume
                                approved_resume_path = f"resume_approved_{job.company.replace(' ', '_')}.docx"
                                self.save_approved_resume(approved_content, approved_resume_path)
                                
                                # Update automation to use approved resume
                                self.automation.profile['resume_path'] = approved_resume_path
                                
                                self.send_progress_update({
                                    'type': 'log',
                                    'message': f"✅ Resume approved by user with score: {approved_score:.2f}",
                                    'level': 'success'
                                })
                            else:
                                # User rejected optimization, use original
                                self.automation.profile['resume_path'] = self.automation.original_resume_path
                                self.send_progress_update({
                                    'type': 'log',
                                    'message': "⚠️ Resume optimization rejected, using original",
                                    'level': 'warning'
                                })
                        else:
                            # Auto-approve optimization
                            if os.path.exists(optimization_result.output_file_path):
                                self.automation.profile['resume_path'] = optimization_result.output_file_path
                                self.send_progress_update({
                                    'type': 'log',
                                    'message': f"✅ Resume auto-approved with score: {optimization_result.optimization_score:.2f}",
                                    'level': 'success'
                                })
            
            # Continue with original application process
            result = original_method(job)
            
            # Send application complete
            self.send_progress_update({
                'type': 'application_complete',
                'success': result.success,
                'result': result.reason
            })
            
            return result
            
        except Exception as e:
            self.send_progress_update({
                'type': 'log',
                'message': f"❌ Error in GUI application process: {e}",
                'level': 'error'
            })
            
            # Fallback to original method
            return original_method(job)
    
    def show_resume_editor_and_wait(self, optimization_result, job: JobListing, job_description: str) -> tuple:
        """Show resume editor and wait for user approval"""
        try:
            # Prepare resume data for editor
            original_content = self.read_resume_content(self.automation.original_resume_path)
            optimized_content = self.read_resume_content(optimization_result.output_file_path)
            
            # Extract keywords from job description
            keywords = getattr(optimization_result.job_requirements, 'ats_keywords', [])
            if not keywords:
                keywords = getattr(optimization_result.job_requirements, 'required_skills', [])
            
            # Create suggestions from optimization result
            suggestions = self.create_suggestions_from_optimization(optimization_result)
            
            # Load data into editor
            self.resume_editor.load_resume_data(
                original_content=original_content,
                optimized_content=optimized_content,
                job_title=job.title,
                company=job.company,
                keywords=keywords,
                optimization_score=optimization_result.optimization_score,
                suggestions=suggestions
            )
            
            # Show editor and pause automation
            self.waiting_for_resume_approval = True
            self.resume_approval_event.clear()
            
            # Show editor in main thread
            self.dashboard.root.after(0, self.resume_editor.show)
            
            # Log pause message
            self.send_progress_update({
                'type': 'log',
                'message': "⏸️ Automation paused for resume review",
                'level': 'warning'
            })
            
            # Wait for user decision
            self.resume_approval_event.wait()
            
            # Return approved content and score
            return self.approved_resume_content, self.approved_resume_score
            
        except Exception as e:
            self.send_progress_update({
                'type': 'log',
                'message': f"❌ Error showing resume editor: {e}",
                'level': 'error'
            })
            return "", 0.0
    
    def create_suggestions_from_optimization(self, optimization_result) -> List[Dict]:
        """Create suggestions list from optimization result"""
        suggestions = []
        
        if hasattr(optimization_result, 'improvements_made'):
            for i, improvement in enumerate(optimization_result.improvements_made):
                suggestions.append({
                    'section': f"Improvement {i+1}",
                    'original_text': "Original content",
                    'suggested_text': improvement,
                    'keywords': [],
                    'reason': "AI optimization suggestion",
                    'approved': True
                })
        
        return suggestions
    
    def read_resume_content(self, file_path: str) -> str:
        """Read resume content from file"""
        try:
            if file_path.endswith('.docx'):
                # Use python-docx to read Word documents
                try:
                    from docx import Document
                    doc = Document(file_path)
                    content = []
                    for paragraph in doc.paragraphs:
                        content.append(paragraph.text)
                    return '\n'.join(content)
                except ImportError:
                    return f"Word document: {os.path.basename(file_path)}\n(Install python-docx to view content)"
            else:
                # Read as text file
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            return f"Error reading file: {e}"
    
    def save_approved_resume(self, content: str, file_path: str):
        """Save approved resume content to file"""
        try:
            # For now, save as text file
            # In production, you'd want to maintain Word format
            text_path = file_path.replace('.docx', '.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update the path to point to the text file
            return text_path
            
        except Exception as e:
            self.send_progress_update({
                'type': 'log',
                'message': f"❌ Error saving approved resume: {e}",
                'level': 'error'
            })
            return None
    
    def on_resume_approved(self, content: str, score: float):
        """Handle resume approval from editor"""
        self.approved_resume_content = content
        self.approved_resume_score = score
        self.waiting_for_resume_approval = False
        self.resume_approval_event.set()
        
        self.send_progress_update({
            'type': 'log',
            'message': "✅ Resume approved, continuing automation",
            'level': 'success'
        })
    
    def on_resume_rejected(self):
        """Handle resume rejection from editor"""
        self.approved_resume_content = ""
        self.approved_resume_score = 0.0
        self.waiting_for_resume_approval = False
        self.resume_approval_event.set()
        
        self.send_progress_update({
            'type': 'log',
            'message': "❌ Resume optimization rejected",
            'level': 'warning'
        })
    
    def run_automation_with_gui_updates(self):
        """Run automation with GUI updates"""
        try:
            self.automation_running = True
            
            # Get job listings
            self.send_progress_update({
                'type': 'log',
                'message': "🔍 Searching for job listings...",
                'level': 'info'
            })
            
            jobs = self.automation.get_job_listings()
            
            if not jobs:
                self.send_progress_update({
                    'type': 'log',
                    'message': "❌ No job listings found",
                    'level': 'error'
                })
                return
            
            # Set total jobs in dashboard
            self.dashboard.set_total_jobs(len(jobs))
            
            self.send_progress_update({
                'type': 'log',
                'message': f"📋 Found {len(jobs)} job listings",
                'level': 'info'
            })
            
            # Process each job
            for i, job in enumerate(jobs):
                if not self.automation_running:
                    break
                
                # Wait if paused
                while self.automation_paused and self.automation_running:
                    time.sleep(0.5)
                
                if not self.automation_running:
                    break
                
                # Apply to job
                try:
                    result = self.automation.apply_to_job(job)
                    
                    # Add delay between applications
                    if i < len(jobs) - 1:  # Not the last job
                        delay = 30  # 30 seconds between applications
                        self.send_progress_update({
                            'type': 'log',
                            'message': f"⏳ Waiting {delay} seconds before next application...",
                            'level': 'info'
                        })
                        
                        for _ in range(delay):
                            if not self.automation_running:
                                break
                            time.sleep(1)
                
                except Exception as e:
                    self.send_progress_update({
                        'type': 'log',
                        'message': f"❌ Error processing job {job.title}: {e}",
                        'level': 'error'
                    })
            
            # Automation complete
            self.send_progress_update({
                'type': 'log',
                'message': "🎉 Automation completed successfully!",
                'level': 'success'
            })
            
        except Exception as e:
            self.send_progress_update({
                'type': 'log',
                'message': f"❌ Automation error: {e}",
                'level': 'error'
            })
        finally:
            self.automation_running = False
            # Update dashboard button states
            self.dashboard.root.after(0, self.dashboard.stop_automation)
    
    def pause_automation(self):
        """Pause the automation"""
        self.automation_paused = True
        self.send_progress_update({
            'type': 'log',
            'message': "⏸️ Automation paused by user",
            'level': 'warning'
        })
    
    def resume_automation(self):
        """Resume the automation"""
        self.automation_paused = False
        self.send_progress_update({
            'type': 'log',
            'message': "▶️ Automation resumed by user",
            'level': 'info'
        })
    
    def stop_automation(self):
        """Stop the automation"""
        self.automation_running = False
        self.automation_paused = False
        
        # If waiting for resume approval, cancel it
        if self.waiting_for_resume_approval:
            self.waiting_for_resume_approval = False
            self.resume_approval_event.set()
        
        self.send_progress_update({
            'type': 'log',
            'message': "⏹️ Automation stopped by user",
            'level': 'error'
        })
    
    def send_progress_update(self, update_data: Dict):
        """Send progress update to GUI"""
        try:
            self.dashboard.progress_queue.put(update_data)
        except Exception as e:
            print(f"Error sending progress update: {e}")

def main():
    """Main entry point for GUI automation"""
    controller = GUIAutomationController()
    controller.start_automation_with_gui()

if __name__ == "__main__":
    main()
