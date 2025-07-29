"""
Real-time Visual Interface for LinkedIn Job Application Automation
Provides live feedback, progress tracking, and interactive resume editing
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
import json
import os

@dataclass
class JobProgress:
    """Data class for tracking job application progress"""
    job_title: str = ""
    company: str = ""
    url: str = ""
    status: str = "pending"  # pending, analyzing, optimizing, applying, completed, failed
    compatibility_score: float = 0.0
    extracted_keywords: List[str] = None
    optimization_score: float = 0.0
    optimization_status: str = ""
    application_result: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.extracted_keywords is None:
            self.extracted_keywords = []

@dataclass
class AutomationStats:
    """Overall automation statistics"""
    total_jobs: int = 0
    processed_jobs: int = 0
    successful_applications: int = 0
    failed_applications: int = 0
    resumes_optimized: int = 0
    average_optimization_score: float = 0.0
    average_compatibility_score: float = 0.0
    start_time: Optional[datetime] = None
    current_job_index: int = 0

class LinkedInGUIDashboard:
    """Main GUI Dashboard for LinkedIn Automation"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LinkedIn Job Application Automation - Real-time Dashboard")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Data structures
        self.current_job = JobProgress()
        self.stats = AutomationStats()
        self.job_history: List[JobProgress] = []
        self.automation_running = False
        self.automation_paused = False
        
        # Communication queues
        self.progress_queue = queue.Queue()
        self.control_queue = queue.Queue()
        
        # Callbacks for automation control
        self.on_pause_callback: Optional[Callable] = None
        self.on_resume_callback: Optional[Callable] = None
        self.on_stop_callback: Optional[Callable] = None
        self.on_resume_editor_callback: Optional[Callable] = None
        
        # GUI Components
        self.setup_gui()
        self.setup_styles()
        
        # Start GUI update loop
        self.root.after(100, self.update_gui)
        
    def setup_styles(self):
        """Configure custom styles for the GUI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#f0f0f0')
        style.configure('Status.TLabel', font=('Arial', 10), background='#f0f0f0')
        style.configure('Success.TLabel', font=('Arial', 10), background='#f0f0f0', foreground='#28a745')
        style.configure('Error.TLabel', font=('Arial', 10), background='#f0f0f0', foreground='#dc3545')
        style.configure('Warning.TLabel', font=('Arial', 10), background='#f0f0f0', foreground='#ffc107')
        
    def setup_gui(self):
        """Setup the main GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="LinkedIn Job Application Automation", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky=tk.W)
        
        # Left Panel - Control and Stats
        self.setup_control_panel(main_frame)
        
        # Center Panel - Current Job Progress
        self.setup_progress_panel(main_frame)
        
        # Right Panel - Job History
        self.setup_history_panel(main_frame)
        
        # Bottom Panel - Logs
        self.setup_log_panel(main_frame)
        
    def setup_control_panel(self, parent):
        """Setup the control and statistics panel"""
        control_frame = ttk.LabelFrame(parent, text="Automation Control", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Control buttons
        self.start_button = ttk.Button(control_frame, text="Start Automation", command=self.start_automation)
        self.start_button.grid(row=0, column=0, pady=5, sticky=tk.W+tk.E)
        
        self.pause_button = ttk.Button(control_frame, text="Pause", command=self.pause_automation, state='disabled')
        self.pause_button.grid(row=1, column=0, pady=5, sticky=tk.W+tk.E)
        
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_automation, state='disabled')
        self.stop_button.grid(row=2, column=0, pady=5, sticky=tk.W+tk.E)
        
        # Separator
        ttk.Separator(control_frame, orient='horizontal').grid(row=3, column=0, sticky=tk.W+tk.E, pady=10)
        
        # Statistics
        stats_label = ttk.Label(control_frame, text="Statistics", style='Header.TLabel')
        stats_label.grid(row=4, column=0, pady=(0, 10), sticky=tk.W)
        
        # Stats display
        self.stats_frame = ttk.Frame(control_frame)
        self.stats_frame.grid(row=5, column=0, sticky=tk.W+tk.E)
        
        self.total_jobs_label = ttk.Label(self.stats_frame, text="Total Jobs: 0", style='Status.TLabel')
        self.total_jobs_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.processed_jobs_label = ttk.Label(self.stats_frame, text="Processed: 0", style='Status.TLabel')
        self.processed_jobs_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.success_rate_label = ttk.Label(self.stats_frame, text="Success Rate: 0%", style='Status.TLabel')
        self.success_rate_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        self.optimization_rate_label = ttk.Label(self.stats_frame, text="Optimization Rate: 0%", style='Status.TLabel')
        self.optimization_rate_label.grid(row=3, column=0, sticky=tk.W, pady=2)
        
        self.avg_optimization_label = ttk.Label(self.stats_frame, text="Avg Optimization: 0.0", style='Status.TLabel')
        self.avg_optimization_label.grid(row=4, column=0, sticky=tk.W, pady=2)
        
        # Separator
        ttk.Separator(control_frame, orient='horizontal').grid(row=6, column=0, sticky=tk.W+tk.E, pady=10)
        
        # Settings
        settings_label = ttk.Label(control_frame, text="Settings", style='Header.TLabel')
        settings_label.grid(row=7, column=0, pady=(0, 10), sticky=tk.W)
        
        self.auto_approve_var = tk.BooleanVar(value=False)
        auto_approve_check = ttk.Checkbutton(control_frame, text="Auto-approve optimizations", 
                                           variable=self.auto_approve_var)
        auto_approve_check.grid(row=8, column=0, sticky=tk.W, pady=2)
        
        self.pause_on_optimization_var = tk.BooleanVar(value=True)
        pause_optimization_check = ttk.Checkbutton(control_frame, text="Pause for resume review", 
                                                 variable=self.pause_on_optimization_var)
        pause_optimization_check.grid(row=9, column=0, sticky=tk.W, pady=2)
        
    def setup_progress_panel(self, parent):
        """Setup the current job progress panel"""
        progress_frame = ttk.LabelFrame(parent, text="Current Job Progress", padding="10")
        progress_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        progress_frame.columnconfigure(0, weight=1)
        
        # Job info
        job_info_frame = ttk.Frame(progress_frame)
        job_info_frame.grid(row=0, column=0, sticky=tk.W+tk.E, pady=(0, 10))
        job_info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(job_info_frame, text="Job Title:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.job_title_label = ttk.Label(job_info_frame, text="No job selected", style='Status.TLabel')
        self.job_title_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(job_info_frame, text="Company:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.company_label = ttk.Label(job_info_frame, text="", style='Status.TLabel')
        self.company_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(job_info_frame, text="Status:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.status_label = ttk.Label(job_info_frame, text="Idle", style='Status.TLabel')
        self.status_label.grid(row=2, column=1, sticky=tk.W)
        
        # Progress bar
        ttk.Label(progress_frame, text="Overall Progress:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress_bar.grid(row=2, column=0, sticky=tk.W+tk.E, pady=(0, 10))
        
        # Analysis results
        analysis_frame = ttk.LabelFrame(progress_frame, text="Job Analysis", padding="5")
        analysis_frame.grid(row=3, column=0, sticky=tk.W+tk.E, pady=5)
        analysis_frame.columnconfigure(1, weight=1)
        
        ttk.Label(analysis_frame, text="Compatibility Score:", style='Status.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.compatibility_score_label = ttk.Label(analysis_frame, text="0.0", style='Status.TLabel')
        self.compatibility_score_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(analysis_frame, text="Keywords Found:", style='Status.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.keywords_count_label = ttk.Label(analysis_frame, text="0", style='Status.TLabel')
        self.keywords_count_label.grid(row=1, column=1, sticky=tk.W)
        
        # Optimization results
        optimization_frame = ttk.LabelFrame(progress_frame, text="Resume Optimization", padding="5")
        optimization_frame.grid(row=4, column=0, sticky=tk.W+tk.E, pady=5)
        optimization_frame.columnconfigure(1, weight=1)
        
        ttk.Label(optimization_frame, text="Optimization Score:", style='Status.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.optimization_score_label = ttk.Label(optimization_frame, text="0.0", style='Status.TLabel')
        self.optimization_score_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(optimization_frame, text="Status:", style='Status.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.optimization_status_label = ttk.Label(optimization_frame, text="Not started", style='Status.TLabel')
        self.optimization_status_label.grid(row=1, column=1, sticky=tk.W)
        
        # Resume editor button
        self.edit_resume_button = ttk.Button(optimization_frame, text="Review & Edit Resume", 
                                           command=self.open_resume_editor, state='disabled')
        self.edit_resume_button.grid(row=2, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E)
        
    def setup_history_panel(self, parent):
        """Setup the job history panel"""
        history_frame = ttk.LabelFrame(parent, text="Job History", padding="10")
        history_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # History tree
        columns = ('Job', 'Company', 'Status', 'Score')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.history_tree.heading('Job', text='Job Title')
        self.history_tree.heading('Company', text='Company')
        self.history_tree.heading('Status', text='Status')
        self.history_tree.heading('Score', text='Opt Score')
        
        self.history_tree.column('Job', width=150)
        self.history_tree.column('Company', width=100)
        self.history_tree.column('Status', width=80)
        self.history_tree.column('Score', width=70)
        
        # Scrollbar for history
        history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        history_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def setup_log_panel(self, parent):
        """Setup the log display panel"""
        log_frame = ttk.LabelFrame(parent, text="Activity Log", padding="10")
        log_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log controls
        log_controls = ttk.Frame(log_frame)
        log_controls.grid(row=1, column=0, sticky=tk.W+tk.E, pady=(5, 0))
        
        ttk.Button(log_controls, text="Clear Log", command=self.clear_log).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(log_controls, text="Save Log", command=self.save_log).grid(row=0, column=1)
        
    def start_automation(self):
        """Start the automation process"""
        self.automation_running = True
        self.automation_paused = False
        
        # Update button states
        self.start_button.config(state='disabled')
        self.pause_button.config(state='normal')
        self.stop_button.config(state='normal')
        
        # Reset stats
        self.stats = AutomationStats()
        self.stats.start_time = datetime.now()
        
        self.log_message("🚀 Automation started", "info")
        
        # Trigger automation start callback if available
        if hasattr(self, 'automation_thread') and self.automation_thread:
            self.automation_thread.start()
    
    def pause_automation(self):
        """Pause/resume the automation process"""
        if self.automation_paused:
            self.automation_paused = False
            self.pause_button.config(text="Pause")
            self.log_message("▶️ Automation resumed", "info")
            if self.on_resume_callback:
                self.on_resume_callback()
        else:
            self.automation_paused = True
            self.pause_button.config(text="Resume")
            self.log_message("⏸️ Automation paused", "warning")
            if self.on_pause_callback:
                self.on_pause_callback()
    
    def stop_automation(self):
        """Stop the automation process"""
        self.automation_running = False
        self.automation_paused = False
        
        # Update button states
        self.start_button.config(state='normal')
        self.pause_button.config(state='disabled', text="Pause")
        self.stop_button.config(state='disabled')
        
        self.log_message("⏹️ Automation stopped", "error")
        
        if self.on_stop_callback:
            self.on_stop_callback()
    
    def open_resume_editor(self):
        """Open the interactive resume editor"""
        if hasattr(self, 'resume_editor') and self.resume_editor:
            self.resume_editor.show()
        else:
            self.log_message("⚠️ Resume editor not available", "warning")
    
    def log_message(self, message: str, level: str = "info"):
        """Add a message to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding based on level
        if level == "error":
            color_tag = "error"
        elif level == "warning":
            color_tag = "warning"
        elif level == "success":
            color_tag = "success"
        else:
            color_tag = "info"
        
        # Configure tags if not already done
        self.log_text.tag_configure("error", foreground="#dc3545")
        self.log_text.tag_configure("warning", foreground="#ffc107")
        self.log_text.tag_configure("success", foreground="#28a745")
        self.log_text.tag_configure("info", foreground="#000000")
        
        # Insert message
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", color_tag)
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        """Save the log to a file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Log File"
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log_message(f"📄 Log saved to {filename}", "success")
            except Exception as e:
                self.log_message(f"❌ Failed to save log: {e}", "error")
    
    def update_gui(self):
        """Update GUI elements with current data"""
        try:
            # Process any pending progress updates
            while not self.progress_queue.empty():
                try:
                    update_data = self.progress_queue.get_nowait()
                    self.process_progress_update(update_data)
                except queue.Empty:
                    break
            
            # Update current job display
            self.update_current_job_display()
            
            # Update statistics
            self.update_statistics_display()
            
        except Exception as e:
            print(f"GUI update error: {e}")
        
        # Schedule next update
        self.root.after(100, self.update_gui)
    
    def process_progress_update(self, update_data: Dict):
        """Process a progress update from the automation"""
        update_type = update_data.get('type', '')
        
        if update_type == 'job_started':
            self.current_job = JobProgress(
                job_title=update_data.get('job_title', ''),
                company=update_data.get('company', ''),
                url=update_data.get('url', ''),
                status='analyzing',
                start_time=datetime.now()
            )
            self.log_message(f"📝 Started processing: {self.current_job.job_title} at {self.current_job.company}")
            
        elif update_type == 'job_analysis':
            self.current_job.compatibility_score = update_data.get('compatibility_score', 0.0)
            self.current_job.extracted_keywords = update_data.get('keywords', [])
            self.current_job.status = 'analyzed'
            self.log_message(f"🔍 Job analysis complete - Compatibility: {self.current_job.compatibility_score:.2f}")
            
        elif update_type == 'optimization_started':
            self.current_job.status = 'optimizing'
            self.current_job.optimization_status = 'In progress'
            self.log_message("🔧 Resume optimization started")
            
        elif update_type == 'optimization_complete':
            self.current_job.optimization_score = update_data.get('optimization_score', 0.0)
            self.current_job.optimization_status = 'Complete'
            self.current_job.status = 'optimized'
            self.edit_resume_button.config(state='normal')
            self.stats.resumes_optimized += 1
            self.log_message(f"✅ Resume optimized - Score: {self.current_job.optimization_score:.2f}")
            
        elif update_type == 'application_complete':
            self.current_job.status = 'completed'
            self.current_job.application_result = update_data.get('result', '')
            self.current_job.end_time = datetime.now()
            
            if update_data.get('success', False):
                self.stats.successful_applications += 1
                self.log_message(f"✅ Application submitted successfully", "success")
            else:
                self.stats.failed_applications += 1
                self.log_message(f"❌ Application failed: {self.current_job.application_result}", "error")
            
            # Add to history
            self.job_history.append(self.current_job)
            self.add_job_to_history(self.current_job)
            
            # Update stats
            self.stats.processed_jobs += 1
            self.edit_resume_button.config(state='disabled')
            
        elif update_type == 'log':
            self.log_message(update_data.get('message', ''), update_data.get('level', 'info'))
    
    def update_current_job_display(self):
        """Update the current job progress display"""
        self.job_title_label.config(text=self.current_job.job_title or "No job selected")
        self.company_label.config(text=self.current_job.company or "")
        self.status_label.config(text=self.current_job.status.title())
        
        # Update compatibility score
        if self.current_job.compatibility_score > 0:
            score_text = f"{self.current_job.compatibility_score:.2f}"
            if self.current_job.compatibility_score >= 0.8:
                self.compatibility_score_label.config(text=score_text, style='Success.TLabel')
            elif self.current_job.compatibility_score >= 0.6:
                self.compatibility_score_label.config(text=score_text, style='Warning.TLabel')
            else:
                self.compatibility_score_label.config(text=score_text, style='Error.TLabel')
        else:
            self.compatibility_score_label.config(text="0.0", style='Status.TLabel')
        
        # Update keywords count
        self.keywords_count_label.config(text=str(len(self.current_job.extracted_keywords)))
        
        # Update optimization score
        if self.current_job.optimization_score > 0:
            opt_score_text = f"{self.current_job.optimization_score:.2f}"
            if self.current_job.optimization_score >= 80:
                self.optimization_score_label.config(text=opt_score_text, style='Success.TLabel')
            elif self.current_job.optimization_score >= 60:
                self.optimization_score_label.config(text=opt_score_text, style='Warning.TLabel')
            else:
                self.optimization_score_label.config(text=opt_score_text, style='Error.TLabel')
        else:
            self.optimization_score_label.config(text="0.0", style='Status.TLabel')
        
        # Update optimization status
        self.optimization_status_label.config(text=self.current_job.optimization_status or "Not started")
        
        # Update progress bar
        if self.stats.total_jobs > 0:
            progress = (self.stats.processed_jobs / self.stats.total_jobs) * 100
            self.progress_bar['value'] = progress
    
    def update_statistics_display(self):
        """Update the statistics display"""
        self.total_jobs_label.config(text=f"Total Jobs: {self.stats.total_jobs}")
        self.processed_jobs_label.config(text=f"Processed: {self.stats.processed_jobs}")
        
        # Success rate
        if self.stats.processed_jobs > 0:
            success_rate = (self.stats.successful_applications / self.stats.processed_jobs) * 100
            self.success_rate_label.config(text=f"Success Rate: {success_rate:.1f}%")
        else:
            self.success_rate_label.config(text="Success Rate: 0%")
        
        # Optimization rate
        if self.stats.processed_jobs > 0:
            opt_rate = (self.stats.resumes_optimized / self.stats.processed_jobs) * 100
            self.optimization_rate_label.config(text=f"Optimization Rate: {opt_rate:.1f}%")
        else:
            self.optimization_rate_label.config(text="Optimization Rate: 0%")
        
        # Average optimization score
        if self.stats.resumes_optimized > 0:
            optimized_jobs = [job for job in self.job_history if job.optimization_score > 0]
            if optimized_jobs:
                avg_score = sum(job.optimization_score for job in optimized_jobs) / len(optimized_jobs)
                self.avg_optimization_label.config(text=f"Avg Optimization: {avg_score:.1f}")
        else:
            self.avg_optimization_label.config(text="Avg Optimization: 0.0")
    
    def add_job_to_history(self, job: JobProgress):
        """Add a job to the history tree"""
        status_icon = "✅" if job.status == "completed" and "success" in job.application_result.lower() else "❌"
        status_text = f"{status_icon} {job.status.title()}"
        
        opt_score = f"{job.optimization_score:.1f}" if job.optimization_score > 0 else "N/A"
        
        self.history_tree.insert('', 'end', values=(
            job.job_title[:20] + "..." if len(job.job_title) > 20 else job.job_title,
            job.company[:15] + "..." if len(job.company) > 15 else job.company,
            status_text,
            opt_score
        ))
        
        # Scroll to bottom
        children = self.history_tree.get_children()
        if children:
            self.history_tree.see(children[-1])
    
    def set_total_jobs(self, total: int):
        """Set the total number of jobs to process"""
        self.stats.total_jobs = total
        self.progress_bar['maximum'] = 100
    
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()

if __name__ == "__main__":
    # Test the dashboard
    dashboard = LinkedInGUIDashboard()
    dashboard.set_total_jobs(10)
    dashboard.run()
