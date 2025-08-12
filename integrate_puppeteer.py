#!/usr/bin/env python3
"""
Integration script showing how to use PuppeteerBridge with your existing GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from puppeteer_bridge import PuppeteerBridge

class PuppeteerLinkedInGUI:
    """Simple GUI demonstrating Puppeteer integration"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Automation with Puppeteer")
        self.root.geometry("600x400")
        
        self.puppeteer_bridge = PuppeteerBridge()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🚀 LinkedIn Automation with Puppeteer", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Job keywords
        ttk.Label(main_frame, text="Job Keywords:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.keywords_var = tk.StringVar(value="python developer")
        keywords_entry = ttk.Entry(main_frame, textvariable=self.keywords_var, width=40)
        keywords_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Location
        ttk.Label(main_frame, text="Location:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.location_var = tk.StringVar(value="remote")
        location_entry = ttk.Entry(main_frame, textvariable=self.location_var, width=40)
        location_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Start button
        self.start_button = ttk.Button(main_frame, text="🚀 Start LinkedIn Automation", 
                                      command=self.start_automation)
        self.start_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Status
        self.status_var = tk.StringVar(value="Ready to start automation")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=("Arial", 10))
        status_label.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Results text
        ttk.Label(main_frame, text="Results:").grid(row=6, column=0, sticky=tk.W, pady=(20, 5))
        self.results_text = tk.Text(main_frame, height=8, width=70)
        self.results_text.grid(row=7, column=0, columnspan=2, pady=5)
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.grid(row=7, column=2, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
    def start_automation(self):
        """Start the LinkedIn automation in a separate thread"""
        if self.puppeteer_bridge.is_automation_running():
            messagebox.showwarning("Warning", "Automation is already running!")
            return
            
        # Disable start button
        self.start_button.config(state='disabled')
        self.progress.start()
        self.status_var.set("Starting LinkedIn automation...")
        self.results_text.delete(1.0, tk.END)
        
        # Start automation in separate thread
        thread = threading.Thread(target=self._run_automation)
        thread.daemon = True
        thread.start()
        
    def _run_automation(self):
        """Run the automation (called in separate thread)"""
        try:
            keywords = self.keywords_var.get()
            location = self.location_var.get()
            
            self.root.after(0, lambda: self.status_var.set(f"Running automation for '{keywords}' in '{location}'..."))
            
            # Start the automation
            success = self.puppeteer_bridge.start_linkedin_automation(keywords, location)
            
            if success:
                self.root.after(0, lambda: self.status_var.set("Automation completed successfully! Loading results..."))
                
                # Get jobs from file
                jobs = self.puppeteer_bridge.get_jobs_from_file()
                
                if jobs:
                    self.root.after(0, lambda: self._display_results(jobs))
                    self.root.after(0, lambda: self.status_var.set(f"Found {len(jobs)} jobs!"))
                else:
                    self.root.after(0, lambda: self.status_var.set("No jobs found"))
                    self.root.after(0, lambda: self.results_text.insert(tk.END, "No jobs were found during this automation run.\n\nThis could be due to:\n- No matching jobs for the search criteria\n- LinkedIn's page structure changed\n- Automation was interrupted\n\nTry running again or check the browser window for any issues."))
            else:
                self.root.after(0, lambda: self.status_var.set("Automation failed. Check console for details."))
                self.root.after(0, lambda: self.results_text.insert(tk.END, "Automation failed. Check the console output above for error details.\n\nCommon issues:\n- LinkedIn login failed\n- Page elements not found\n- Network connectivity issues\n\nTry running again or check your credentials."))
                
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            self.root.after(0, lambda: self.results_text.insert(tk.END, f"An error occurred: {str(e)}\n\nPlease check the console for more details."))
            
        finally:
            # Re-enable start button and stop progress
            self.root.after(0, lambda: self.start_button.config(state='normal'))
            self.root.after(0, lambda: self.progress.stop())
    
    def _display_results(self, jobs):
        """Display the job results in the text area"""
        self.results_text.delete(1.0, tk.END)
        
        if not jobs:
            self.results_text.insert(tk.END, "No jobs found.")
            return
            
        self.results_text.insert(tk.END, f"Found {len(jobs)} jobs:\n\n")
        
        for i, job in enumerate(jobs, 1):
            self.results_text.insert(tk.END, f"Job {i}:\n")
            self.results_text.insert(tk.END, f"Title: {job.get('title', 'N/A')}\n")
            self.results_text.insert(tk.END, f"Company: {job.get('company', 'N/A')}\n")
            self.results_text.insert(tk.END, f"Location: {job.get('location', 'N/A')}\n")
            self.results_text.insert(tk.END, f"URL: {job.get('url', 'N/A')}\n")
            
            # Show first 200 characters of description
            description = job.get('description', 'N/A')
            if len(description) > 200:
                description = description[:200] + "..."
            self.results_text.insert(tk.END, f"Description: {description}\n")
            
            self.results_text.insert(tk.END, "-" * 50 + "\n\n")

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = PuppeteerLinkedInGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
