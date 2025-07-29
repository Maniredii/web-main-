"""
LinkedIn Job Application Automation - GUI Launcher
Easy-to-use launcher for the visual automation interface
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import subprocess
from pathlib import Path

class AutomationLauncher:
    """Launcher interface for LinkedIn automation with GUI"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LinkedIn Automation Launcher")
        self.root.geometry("800x600")
        self.root.configure(bg='#f8f9fa')

        # Configuration
        self.config = self.load_config()

        # Setup GUI
        self.setup_gui()

        # Check dependencies
        self.check_dependencies()

    def safe_int_conversion(self, value, default=0):
        """Safely convert value to integer, handling lists and strings"""
        if isinstance(value, list):
            # If it's a list, take the first value
            value = value[0] if value else default
        elif isinstance(value, str):
            # If it's a string that looks like a list, extract the first number
            if value.startswith('[') and ',' in value:
                try:
                    value = int(value.strip('[]').split(',')[0].strip())
                except (ValueError, IndexError):
                    value = default
            else:
                try:
                    value = int(value)
                except ValueError:
                    value = default
        elif not isinstance(value, int):
            value = default

        return value
    
    def load_config(self) -> dict:
        """Load configuration from file"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
        
        # Default configuration
        return {
            "linkedin": {
                "email": "",
                "password": "",
                "job_search_keywords": ["Python Developer", "Software Engineer"],
                "location": "United States",
                "experience_level": "Mid-Senior level"
            },
            "automation": {
                "max_applications": 10,
                "delay_between_applications": 30,
                "headless_mode": False,
                "enable_resume_optimization": True,
                "pause_on_optimization": True,
                "auto_approve_optimizations": False
            },
            "ollama": {
                "endpoint": "http://localhost:11434",
                "model": "qwen2.5:7b",
                "timeout": 30
            },
            "resume": {
                "resume_path": "sample resume.docx",
                "cover_letter_path": ""
            }
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
            return False
    
    def setup_gui(self):
        """Setup the launcher GUI"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="LinkedIn Job Application Automation", 
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, text="AI-Powered Resume Optimization & Real-time Visual Interface", 
                                  font=('Arial', 12))
        subtitle_label.pack(pady=(0, 30))
        
        # Create notebook for configuration tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Setup configuration tabs
        self.setup_linkedin_tab()
        self.setup_automation_tab()
        self.setup_resume_tab()
        self.setup_ollama_tab()
        
        # Control buttons
        self.setup_control_buttons(main_frame)
        
        # Status bar
        self.setup_status_bar(main_frame)
    
    def setup_linkedin_tab(self):
        """Setup LinkedIn configuration tab"""
        linkedin_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(linkedin_frame, text="LinkedIn Settings")
        
        # LinkedIn credentials
        cred_frame = ttk.LabelFrame(linkedin_frame, text="LinkedIn Credentials", padding="10")
        cred_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(cred_frame, text="Email:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.email_var = tk.StringVar(value=self.config.get("linkedin", {}).get("email", ""))
        email_entry = ttk.Entry(cred_frame, textvariable=self.email_var, width=40)
        email_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=2)
        
        ttk.Label(cred_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.password_var = tk.StringVar(value=self.config.get("linkedin", {}).get("password", ""))
        password_entry = ttk.Entry(cred_frame, textvariable=self.password_var, show="*", width=40)
        password_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=2)
        
        cred_frame.columnconfigure(1, weight=1)
        
        # Job search settings
        search_frame = ttk.LabelFrame(linkedin_frame, text="Job Search Settings", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(search_frame, text="Keywords (one per line):").pack(anchor=tk.W)
        self.keywords_text = tk.Text(search_frame, height=4, width=50)
        keywords = self.config.get("linkedin", {}).get("job_search_keywords", [])
        self.keywords_text.insert(1.0, '\n'.join(keywords))
        self.keywords_text.pack(fill=tk.X, pady=(5, 10))
        
        location_frame = ttk.Frame(search_frame)
        location_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(location_frame, text="Location:").pack(side=tk.LEFT, padx=(0, 10))
        self.location_var = tk.StringVar(value=self.config.get("linkedin", {}).get("location", ""))
        location_entry = ttk.Entry(location_frame, textvariable=self.location_var, width=30)
        location_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        exp_frame = ttk.Frame(search_frame)
        exp_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(exp_frame, text="Experience Level:").pack(side=tk.LEFT, padx=(0, 10))
        self.experience_var = tk.StringVar(value=self.config.get("linkedin", {}).get("experience_level", ""))
        experience_combo = ttk.Combobox(exp_frame, textvariable=self.experience_var, 
                                       values=["Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"])
        experience_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def setup_automation_tab(self):
        """Setup automation configuration tab"""
        automation_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(automation_frame, text="Automation Settings")
        
        # Basic settings
        basic_frame = ttk.LabelFrame(automation_frame, text="Basic Settings", padding="10")
        basic_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Max applications
        max_frame = ttk.Frame(basic_frame)
        max_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(max_frame, text="Maximum Applications:").pack(side=tk.LEFT, padx=(0, 10))
        self.max_apps_var = tk.StringVar(value=str(self.config.get("automation", {}).get("max_applications", 10)))
        max_apps_spin = ttk.Spinbox(max_frame, from_=1, to=100, textvariable=self.max_apps_var, width=10)
        max_apps_spin.pack(side=tk.LEFT)
        
        # Delay
        delay_frame = ttk.Frame(basic_frame)
        delay_frame.pack(fill=tk.X, pady=5)

        ttk.Label(delay_frame, text="Delay Between Applications (seconds):").pack(side=tk.LEFT, padx=(0, 10))

        # Handle delay value safely using helper function
        delay_value = self.safe_int_conversion(
            self.config.get("automation", {}).get("delay_between_applications", 30),
            default=30
        )
        self.delay_var = tk.StringVar(value=str(delay_value))
        delay_spin = ttk.Spinbox(delay_frame, from_=10, to=300, textvariable=self.delay_var, width=10)
        delay_spin.pack(side=tk.LEFT)
        
        # Browser settings
        browser_frame = ttk.LabelFrame(automation_frame, text="Browser Settings", padding="10")
        browser_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.headless_var = tk.BooleanVar(value=self.config.get("automation", {}).get("headless_mode", False))
        headless_check = ttk.Checkbutton(browser_frame, text="Run in headless mode (no browser window)", 
                                        variable=self.headless_var)
        headless_check.pack(anchor=tk.W, pady=2)
        
        # Resume optimization settings
        resume_opt_frame = ttk.LabelFrame(automation_frame, text="Resume Optimization", padding="10")
        resume_opt_frame.pack(fill=tk.X)
        
        self.enable_optimization_var = tk.BooleanVar(value=self.config.get("automation", {}).get("enable_resume_optimization", True))
        enable_opt_check = ttk.Checkbutton(resume_opt_frame, text="Enable AI resume optimization", 
                                          variable=self.enable_optimization_var)
        enable_opt_check.pack(anchor=tk.W, pady=2)
        
        self.pause_on_opt_var = tk.BooleanVar(value=self.config.get("automation", {}).get("pause_on_optimization", True))
        pause_opt_check = ttk.Checkbutton(resume_opt_frame, text="Pause for manual resume review", 
                                         variable=self.pause_on_opt_var)
        pause_opt_check.pack(anchor=tk.W, pady=2)
        
        self.auto_approve_var = tk.BooleanVar(value=self.config.get("automation", {}).get("auto_approve_optimizations", False))
        auto_approve_check = ttk.Checkbutton(resume_opt_frame, text="Auto-approve all optimizations", 
                                           variable=self.auto_approve_var)
        auto_approve_check.pack(anchor=tk.W, pady=2)
    
    def setup_resume_tab(self):
        """Setup resume configuration tab"""
        resume_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(resume_frame, text="Resume & Documents")
        
        # Resume file
        resume_file_frame = ttk.LabelFrame(resume_frame, text="Resume File", padding="10")
        resume_file_frame.pack(fill=tk.X, pady=(0, 20))
        
        resume_path_frame = ttk.Frame(resume_file_frame)
        resume_path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(resume_path_frame, text="Resume Path:").pack(anchor=tk.W)
        
        path_entry_frame = ttk.Frame(resume_path_frame)
        path_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.resume_path_var = tk.StringVar(value=self.config.get("resume", {}).get("resume_path", ""))
        resume_path_entry = ttk.Entry(path_entry_frame, textvariable=self.resume_path_var)
        resume_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(path_entry_frame, text="Browse", 
                  command=self.browse_resume_file).pack(side=tk.RIGHT)
        
        # Resume status
        self.resume_status_label = ttk.Label(resume_file_frame, text="", foreground="gray")
        self.resume_status_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Cover letter (optional)
        cover_frame = ttk.LabelFrame(resume_frame, text="Cover Letter (Optional)", padding="10")
        cover_frame.pack(fill=tk.X)
        
        cover_path_frame = ttk.Frame(cover_frame)
        cover_path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(cover_path_frame, text="Cover Letter Path:").pack(anchor=tk.W)
        
        cover_entry_frame = ttk.Frame(cover_path_frame)
        cover_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.cover_path_var = tk.StringVar(value=self.config.get("resume", {}).get("cover_letter_path", ""))
        cover_path_entry = ttk.Entry(cover_entry_frame, textvariable=self.cover_path_var)
        cover_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(cover_entry_frame, text="Browse", 
                  command=self.browse_cover_file).pack(side=tk.RIGHT)
        
        # Update resume status
        self.update_resume_status()
    
    def setup_ollama_tab(self):
        """Setup Ollama configuration tab"""
        ollama_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(ollama_frame, text="AI Settings (Ollama)")
        
        # Ollama connection
        connection_frame = ttk.LabelFrame(ollama_frame, text="Ollama Connection", padding="10")
        connection_frame.pack(fill=tk.X, pady=(0, 20))
        
        endpoint_frame = ttk.Frame(connection_frame)
        endpoint_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(endpoint_frame, text="Ollama Endpoint:").pack(side=tk.LEFT, padx=(0, 10))
        self.ollama_endpoint_var = tk.StringVar(value=self.config.get("ollama", {}).get("endpoint", ""))
        endpoint_entry = ttk.Entry(endpoint_frame, textvariable=self.ollama_endpoint_var, width=30)
        endpoint_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(endpoint_frame, text="Test Connection", 
                  command=self.test_ollama_connection).pack(side=tk.RIGHT)
        
        model_frame = ttk.Frame(connection_frame)
        model_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(model_frame, text="Model:").pack(side=tk.LEFT, padx=(0, 10))
        self.ollama_model_var = tk.StringVar(value=self.config.get("ollama", {}).get("model", ""))
        model_entry = ttk.Entry(model_frame, textvariable=self.ollama_model_var, width=20)
        model_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Ollama status
        self.ollama_status_label = ttk.Label(connection_frame, text="", foreground="gray")
        self.ollama_status_label.pack(anchor=tk.W, pady=(10, 0))
        
        # AI features info
        info_frame = ttk.LabelFrame(ollama_frame, text="AI Features", padding="10")
        info_frame.pack(fill=tk.X)
        
        info_text = """AI-Powered Features:
• Intelligent job compatibility analysis
• Automatic resume optimization for each job
• ATS-friendly keyword integration
• Natural language content enhancement
• Real-time optimization scoring

Note: Ollama must be installed and running for AI features to work.
Without Ollama, basic automation will still function."""
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(anchor=tk.W)
    
    def setup_control_buttons(self, parent):
        """Setup control buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left side buttons
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)
        
        ttk.Button(left_buttons, text="Save Configuration", 
                  command=self.save_configuration).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(left_buttons, text="Load Configuration", 
                  command=self.load_configuration).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(left_buttons, text="Test Resume Optimization", 
                  command=self.test_resume_optimization).pack(side=tk.LEFT)
        
        # Right side buttons
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(right_buttons, text="Start Automation", 
                  command=self.start_automation, 
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(right_buttons, text="Start Without GUI", 
                  command=self.start_automation_no_gui).pack(side=tk.RIGHT)
    
    def setup_status_bar(self, parent):
        """Setup status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="Ready to start automation", 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X)
    
    def browse_resume_file(self):
        """Browse for resume file"""
        filename = filedialog.askopenfilename(
            title="Select Resume File",
            filetypes=[
                ("Word documents", "*.docx"),
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.resume_path_var.set(filename)
            self.update_resume_status()
    
    def browse_cover_file(self):
        """Browse for cover letter file"""
        filename = filedialog.askopenfilename(
            title="Select Cover Letter File",
            filetypes=[
                ("Word documents", "*.docx"),
                ("PDF files", "*.pdf"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.cover_path_var.set(filename)
    
    def update_resume_status(self):
        """Update resume file status"""
        resume_path = self.resume_path_var.get()
        if resume_path and os.path.exists(resume_path):
            file_size = os.path.getsize(resume_path) / 1024  # KB
            self.resume_status_label.config(text=f"✅ File found ({file_size:.1f} KB)", foreground="green")
        elif resume_path:
            self.resume_status_label.config(text="❌ File not found", foreground="red")
        else:
            self.resume_status_label.config(text="No file selected", foreground="gray")
    
    def test_ollama_connection(self):
        """Test Ollama connection"""
        try:
            import requests
            endpoint = self.ollama_endpoint_var.get()
            response = requests.get(f"{endpoint}/api/tags", timeout=5)
            if response.status_code == 200:
                self.ollama_status_label.config(text="✅ Connection successful", foreground="green")
            else:
                self.ollama_status_label.config(text="❌ Connection failed", foreground="red")
        except Exception as e:
            self.ollama_status_label.config(text=f"❌ Error: {str(e)[:50]}...", foreground="red")
    
    def save_configuration(self):
        """Save current configuration"""
        # Update config with current values
        self.config["linkedin"]["email"] = self.email_var.get()
        self.config["linkedin"]["password"] = self.password_var.get()
        self.config["linkedin"]["job_search_keywords"] = [
            line.strip() for line in self.keywords_text.get(1.0, tk.END).strip().split('\n') if line.strip()
        ]
        self.config["linkedin"]["location"] = self.location_var.get()
        self.config["linkedin"]["experience_level"] = self.experience_var.get()
        
        # Safely convert values with error handling
        self.config["automation"]["max_applications"] = self.safe_int_conversion(self.max_apps_var.get(), 10)
        self.config["automation"]["delay_between_applications"] = self.safe_int_conversion(self.delay_var.get(), 30)

        self.config["automation"]["headless_mode"] = self.headless_var.get()
        self.config["automation"]["enable_resume_optimization"] = self.enable_optimization_var.get()
        self.config["automation"]["pause_on_optimization"] = self.pause_on_opt_var.get()
        self.config["automation"]["auto_approve_optimizations"] = self.auto_approve_var.get()
        
        self.config["resume"]["resume_path"] = self.resume_path_var.get()
        self.config["resume"]["cover_letter_path"] = self.cover_path_var.get()
        
        self.config["ollama"]["endpoint"] = self.ollama_endpoint_var.get()
        self.config["ollama"]["model"] = self.ollama_model_var.get()
        
        if self.save_config():
            self.status_label.config(text="Configuration saved successfully")
            messagebox.showinfo("Success", "Configuration saved successfully!")
    
    def load_configuration(self):
        """Load configuration from file"""
        filename = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.config = json.load(f)
                self.update_gui_from_config()
                self.status_label.config(text=f"Configuration loaded from {filename}")
                messagebox.showinfo("Success", "Configuration loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def update_gui_from_config(self):
        """Update GUI elements from loaded configuration"""
        # Update all GUI elements with config values
        linkedin_config = self.config.get("linkedin", {})
        self.email_var.set(linkedin_config.get("email", ""))
        self.password_var.set(linkedin_config.get("password", ""))
        
        keywords = linkedin_config.get("job_search_keywords", [])
        self.keywords_text.delete(1.0, tk.END)
        self.keywords_text.insert(1.0, '\n'.join(keywords))
        
        self.location_var.set(linkedin_config.get("location", ""))
        self.experience_var.set(linkedin_config.get("experience_level", ""))
        
        automation_config = self.config.get("automation", {})
        self.max_apps_var.set(str(automation_config.get("max_applications", 10)))

        # Handle delay value safely using helper function
        delay_value = self.safe_int_conversion(automation_config.get("delay_between_applications", 30), 30)
        self.delay_var.set(str(delay_value))
        self.headless_var.set(automation_config.get("headless_mode", False))
        self.enable_optimization_var.set(automation_config.get("enable_resume_optimization", True))
        self.pause_on_opt_var.set(automation_config.get("pause_on_optimization", True))
        self.auto_approve_var.set(automation_config.get("auto_approve_optimizations", False))
        
        resume_config = self.config.get("resume", {})
        self.resume_path_var.set(resume_config.get("resume_path", ""))
        self.cover_path_var.set(resume_config.get("cover_letter_path", ""))
        
        ollama_config = self.config.get("ollama", {})
        self.ollama_endpoint_var.set(ollama_config.get("endpoint", ""))
        self.ollama_model_var.set(ollama_config.get("model", ""))
        
        self.update_resume_status()
    
    def test_resume_optimization(self):
        """Test resume optimization functionality"""
        try:
            # Save current config first
            self.save_configuration()
            
            # Run test
            result = subprocess.run([sys.executable, "test_resume_optimization.py"], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                messagebox.showinfo("Test Results", "Resume optimization test completed successfully!\n\nCheck the console output for detailed results.")
            else:
                messagebox.showerror("Test Failed", f"Resume optimization test failed:\n\n{result.stderr}")
                
        except subprocess.TimeoutExpired:
            messagebox.showerror("Test Timeout", "Resume optimization test timed out after 60 seconds.")
        except Exception as e:
            messagebox.showerror("Test Error", f"Error running test: {e}")
    
    def check_dependencies(self):
        """Check if required dependencies are available"""
        missing_deps = []
        
        try:
            import selenium
        except ImportError:
            missing_deps.append("selenium")
        
        try:
            import requests
        except ImportError:
            missing_deps.append("requests")
        
        if missing_deps:
            messagebox.showwarning("Missing Dependencies", 
                                 f"Missing required packages: {', '.join(missing_deps)}\n\n"
                                 "Please install them using:\n"
                                 f"pip install {' '.join(missing_deps)}")
    
    def start_automation(self):
        """Start automation with GUI"""
        if not self.validate_configuration():
            return
        
        # Save configuration
        self.save_configuration()
        
        # Hide launcher and start GUI automation
        self.root.withdraw()
        
        try:
            from gui_automation_controller import GUIAutomationController
            controller = GUIAutomationController()
            controller.start_automation_with_gui()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start automation: {e}")
        finally:
            self.root.deiconify()  # Show launcher again
    
    def start_automation_no_gui(self):
        """Start automation without GUI (command line mode)"""
        if not self.validate_configuration():
            return
        
        # Save configuration
        self.save_configuration()
        
        try:
            # Run automation in separate process
            subprocess.Popen([sys.executable, "linkedin_ollama_automation.py"])
            self.status_label.config(text="Automation started in background")
            messagebox.showinfo("Automation Started", "LinkedIn automation started in command-line mode.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start automation: {e}")
    
    def validate_configuration(self) -> bool:
        """Validate configuration before starting"""
        errors = []
        
        # Check LinkedIn credentials
        if not self.email_var.get().strip():
            errors.append("LinkedIn email is required")
        
        if not self.password_var.get().strip():
            errors.append("LinkedIn password is required")
        
        # Check resume file
        resume_path = self.resume_path_var.get().strip()
        if not resume_path:
            errors.append("Resume file is required")
        elif not os.path.exists(resume_path):
            errors.append("Resume file does not exist")
        
        # Check job search keywords
        keywords = [line.strip() for line in self.keywords_text.get(1.0, tk.END).strip().split('\n') if line.strip()]
        if not keywords:
            errors.append("At least one job search keyword is required")
        
        if errors:
            messagebox.showerror("Configuration Error", "\n".join(errors))
            return False
        
        return True
    
    def run(self):
        """Start the launcher"""
        self.root.mainloop()

def main():
    """Main entry point"""
    launcher = AutomationLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
