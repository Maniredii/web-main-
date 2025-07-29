"""
Interactive Resume Editor for LinkedIn Automation
Provides side-by-side comparison and real-time editing capabilities
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Tuple
import difflib
import re
import json
import os

@dataclass
class ResumeSection:
    """Data class for resume sections"""
    title: str
    original_content: str
    optimized_content: str
    user_content: str
    keywords_added: List[str]
    modifications: List[str]
    approved: bool = False

@dataclass
class OptimizationSuggestion:
    """Data class for optimization suggestions"""
    section: str
    original_text: str
    suggested_text: str
    keywords: List[str]
    reason: str
    approved: bool = False

class InteractiveResumeEditor:
    """Interactive Resume Editor with side-by-side comparison"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.visible = False
        
        # Resume data
        self.original_resume: Dict = {}
        self.optimized_resume: Dict = {}
        self.user_resume: Dict = {}
        self.resume_sections: List[ResumeSection] = []
        self.optimization_suggestions: List[OptimizationSuggestion] = []
        
        # Current optimization data
        self.job_title = ""
        self.company = ""
        self.job_keywords: List[str] = []
        self.optimization_score = 0.0
        
        # Callbacks
        self.on_approve_callback: Optional[Callable] = None
        self.on_reject_callback: Optional[Callable] = None
        self.on_save_callback: Optional[Callable] = None
        
        # GUI components
        self.text_widgets: Dict[str, tk.Text] = {}
        self.suggestion_vars: Dict[str, tk.BooleanVar] = {}
        
    def create_window(self):
        """Create the editor window"""
        if self.window:
            self.window.destroy()
        
        self.window = tk.Toplevel(self.parent.root if self.parent else None)
        self.window.title("Interactive Resume Editor")
        self.window.geometry("1600x1000")
        self.window.configure(bg='#f8f9fa')
        
        # Make window modal
        self.window.transient(self.parent.root if self.parent else None)
        self.window.grab_set()
        
        # Setup the editor interface
        self.setup_editor_interface()
        
        # Center the window
        self.center_window()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
    
    def setup_editor_interface(self):
        """Setup the main editor interface"""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.setup_header(main_frame)
        
        # Main content area with notebook
        self.setup_content_area(main_frame)
        
        # Footer with controls
        self.setup_footer(main_frame)
    
    def setup_header(self, parent):
        """Setup the header with job information"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame, text="Resume Optimization Editor", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        # Job info
        job_info_frame = ttk.Frame(header_frame)
        job_info_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.job_info_label = ttk.Label(job_info_frame, text="No job selected", 
                                       font=('Arial', 10))
        self.job_info_label.pack(anchor=tk.W)
        
        self.optimization_info_label = ttk.Label(job_info_frame, text="Optimization Score: 0.0", 
                                                font=('Arial', 10))
        self.optimization_info_label.pack(anchor=tk.W)
        
        # Separator
        ttk.Separator(header_frame, orient='horizontal').pack(fill=tk.X, pady=(10, 0))
    
    def setup_content_area(self, parent):
        """Setup the main content area with tabs"""
        # Create notebook for different views
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Side-by-side comparison tab
        self.setup_comparison_tab()
        
        # Suggestions review tab
        self.setup_suggestions_tab()
        
        # Keywords analysis tab
        self.setup_keywords_tab()
        
        # Full document preview tab
        self.setup_preview_tab()
    
    def setup_comparison_tab(self):
        """Setup the side-by-side comparison tab"""
        comparison_frame = ttk.Frame(self.notebook)
        self.notebook.add(comparison_frame, text="Side-by-Side Comparison")
        
        # Create paned window for resizable sections
        paned_window = ttk.PanedWindow(comparison_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Original resume panel
        original_frame = ttk.LabelFrame(paned_window, text="Original Resume", padding="5")
        paned_window.add(original_frame, weight=1)
        
        self.original_text = scrolledtext.ScrolledText(original_frame, wrap=tk.WORD, 
                                                      font=('Consolas', 10), state='disabled')
        self.original_text.pack(fill=tk.BOTH, expand=True)
        
        # Optimized resume panel
        optimized_frame = ttk.LabelFrame(paned_window, text="AI-Optimized Resume", padding="5")
        paned_window.add(optimized_frame, weight=1)
        
        self.optimized_text = scrolledtext.ScrolledText(optimized_frame, wrap=tk.WORD, 
                                                       font=('Consolas', 10))
        self.optimized_text.pack(fill=tk.BOTH, expand=True)
        
        # Bind text change events
        self.optimized_text.bind('<KeyRelease>', self.on_text_change)
        self.optimized_text.bind('<Button-1>', self.on_text_change)
        
        # Configure text highlighting
        self.setup_text_highlighting()
    
    def setup_suggestions_tab(self):
        """Setup the suggestions review tab"""
        suggestions_frame = ttk.Frame(self.notebook)
        self.notebook.add(suggestions_frame, text="Review Suggestions")
        
        # Create scrollable frame
        canvas = tk.Canvas(suggestions_frame)
        scrollbar = ttk.Scrollbar(suggestions_frame, orient="vertical", command=canvas.yview)
        self.suggestions_scrollable_frame = ttk.Frame(canvas)
        
        self.suggestions_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.suggestions_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Instructions
        instructions = ttk.Label(self.suggestions_scrollable_frame, 
                                text="Review each optimization suggestion below. Check the boxes to approve changes.",
                                font=('Arial', 10))
        instructions.pack(anchor=tk.W, padx=10, pady=10)
    
    def setup_keywords_tab(self):
        """Setup the keywords analysis tab"""
        keywords_frame = ttk.Frame(self.notebook)
        self.notebook.add(keywords_frame, text="Keywords Analysis")
        
        # Create two columns
        columns_frame = ttk.Frame(keywords_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Job keywords column
        job_keywords_frame = ttk.LabelFrame(columns_frame, text="Job Keywords", padding="10")
        job_keywords_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.job_keywords_text = scrolledtext.ScrolledText(job_keywords_frame, height=15, 
                                                          font=('Arial', 10), state='disabled')
        self.job_keywords_text.pack(fill=tk.BOTH, expand=True)
        
        # Resume keywords column
        resume_keywords_frame = ttk.LabelFrame(columns_frame, text="Resume Keywords", padding="10")
        resume_keywords_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.resume_keywords_text = scrolledtext.ScrolledText(resume_keywords_frame, height=15, 
                                                             font=('Arial', 10), state='disabled')
        self.resume_keywords_text.pack(fill=tk.BOTH, expand=True)
        
        # Keywords matching statistics
        stats_frame = ttk.LabelFrame(keywords_frame, text="Keyword Matching Statistics", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.keyword_stats_label = ttk.Label(stats_frame, text="No analysis available", 
                                           font=('Arial', 10))
        self.keyword_stats_label.pack(anchor=tk.W)
    
    def setup_preview_tab(self):
        """Setup the full document preview tab"""
        preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(preview_frame, text="Final Preview")
        
        # Preview controls
        controls_frame = ttk.Frame(preview_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(controls_frame, text="Final Resume Preview:", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        # Export button
        ttk.Button(controls_frame, text="Export to Word", 
                  command=self.export_to_word).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Preview text
        self.preview_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD, 
                                                     font=('Arial', 11), state='disabled')
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    def setup_footer(self, parent):
        """Setup the footer with action buttons"""
        footer_frame = ttk.Frame(parent)
        footer_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Left side - ATS score and stats
        left_frame = ttk.Frame(footer_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.ats_score_label = ttk.Label(left_frame, text="ATS Score: 0.0/100", 
                                        font=('Arial', 12, 'bold'))
        self.ats_score_label.pack(anchor=tk.W)
        
        self.changes_label = ttk.Label(left_frame, text="Changes: 0 modifications", 
                                      font=('Arial', 10))
        self.changes_label.pack(anchor=tk.W)
        
        # Right side - action buttons
        buttons_frame = ttk.Frame(footer_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        # Action buttons
        ttk.Button(buttons_frame, text="Revert All", 
                  command=self.revert_all_changes).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="Apply Suggestions", 
                  command=self.apply_selected_suggestions).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="Cancel", 
                  command=self.cancel_editing).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="Save & Continue", 
                  command=self.save_and_continue, 
                  style='Accent.TButton').pack(side=tk.LEFT)
    
    def setup_text_highlighting(self):
        """Setup text highlighting for changes"""
        # Configure text tags for highlighting
        self.original_text.tag_configure("removed", background="#ffebee", foreground="#c62828")
        self.original_text.tag_configure("unchanged", background="white", foreground="black")
        
        self.optimized_text.tag_configure("added", background="#e8f5e8", foreground="#2e7d32")
        self.optimized_text.tag_configure("modified", background="#fff3e0", foreground="#ef6c00")
        self.optimized_text.tag_configure("unchanged", background="white", foreground="black")
        self.optimized_text.tag_configure("keyword", background="#e3f2fd", foreground="#1565c0", font=('Consolas', 10, 'bold'))
    
    def load_resume_data(self, original_content: str, optimized_content: str, 
                        job_title: str, company: str, keywords: List[str], 
                        optimization_score: float, suggestions: List[Dict] = None):
        """Load resume data for editing"""
        self.job_title = job_title
        self.company = company
        self.job_keywords = keywords
        self.optimization_score = optimization_score
        
        # Store content
        self.original_resume = {"content": original_content}
        self.optimized_resume = {"content": optimized_content}
        self.user_resume = {"content": optimized_content}  # Start with optimized version
        
        # Process suggestions
        if suggestions:
            self.optimization_suggestions = [
                OptimizationSuggestion(**suggestion) for suggestion in suggestions
            ]
        
        # Update UI
        self.update_interface()
    
    def update_interface(self):
        """Update the interface with current data"""
        if not self.window:
            return
        
        # Update header
        job_text = f"Job: {self.job_title} at {self.company}"
        self.job_info_label.config(text=job_text)
        
        score_text = f"Optimization Score: {self.optimization_score:.1f}/100"
        self.optimization_info_label.config(text=score_text)
        
        # Update comparison tab
        self.update_comparison_view()
        
        # Update suggestions tab
        self.update_suggestions_view()
        
        # Update keywords tab
        self.update_keywords_view()
        
        # Update preview tab
        self.update_preview()
        
        # Update footer
        self.update_footer()
    
    def update_comparison_view(self):
        """Update the side-by-side comparison view"""
        # Clear existing content
        self.original_text.config(state='normal')
        self.original_text.delete(1.0, tk.END)
        self.optimized_text.delete(1.0, tk.END)
        
        # Insert original content
        original_content = self.original_resume.get("content", "")
        self.original_text.insert(1.0, original_content)
        self.original_text.config(state='disabled')
        
        # Insert optimized content
        optimized_content = self.user_resume.get("content", "")
        self.optimized_text.insert(1.0, optimized_content)
        
        # Highlight differences
        self.highlight_differences()
        
        # Highlight keywords
        self.highlight_keywords()
    
    def highlight_differences(self):
        """Highlight differences between original and optimized text"""
        original_lines = self.original_resume.get("content", "").split('\n')
        optimized_lines = self.user_resume.get("content", "").split('\n')
        
        # Use difflib to find differences
        differ = difflib.unified_diff(original_lines, optimized_lines, lineterm='')
        
        # Process differences and highlight
        # This is a simplified version - in practice, you'd want more sophisticated highlighting
        for line in differ:
            if line.startswith('+ '):
                # Added line - highlight in optimized text
                pass
            elif line.startswith('- '):
                # Removed line - highlight in original text
                pass
    
    def highlight_keywords(self):
        """Highlight job keywords in the optimized text"""
        content = self.optimized_text.get(1.0, tk.END)
        
        for keyword in self.job_keywords:
            # Find all occurrences of the keyword
            start_pos = 1.0
            while True:
                pos = self.optimized_text.search(keyword, start_pos, tk.END, nocase=True)
                if not pos:
                    break
                
                end_pos = f"{pos}+{len(keyword)}c"
                self.optimized_text.tag_add("keyword", pos, end_pos)
                start_pos = end_pos
    
    def update_suggestions_view(self):
        """Update the suggestions review tab"""
        # Clear existing suggestions
        for widget in self.suggestions_scrollable_frame.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                widget.destroy()
        
        # Add suggestions
        for i, suggestion in enumerate(self.optimization_suggestions):
            self.create_suggestion_widget(suggestion, i)
    
    def create_suggestion_widget(self, suggestion: OptimizationSuggestion, index: int):
        """Create a widget for a single suggestion"""
        suggestion_frame = ttk.LabelFrame(self.suggestions_scrollable_frame, 
                                        text=f"Suggestion {index + 1}: {suggestion.section}", 
                                        padding="10")
        suggestion_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Checkbox for approval
        var = tk.BooleanVar(value=suggestion.approved)
        self.suggestion_vars[f"suggestion_{index}"] = var
        
        checkbox = ttk.Checkbutton(suggestion_frame, text="Apply this suggestion", 
                                  variable=var, command=lambda: self.on_suggestion_toggle(index))
        checkbox.pack(anchor=tk.W, pady=(0, 5))
        
        # Reason
        reason_label = ttk.Label(suggestion_frame, text=f"Reason: {suggestion.reason}", 
                               font=('Arial', 9))
        reason_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Original text
        ttk.Label(suggestion_frame, text="Original:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        original_text = tk.Text(suggestion_frame, height=3, wrap=tk.WORD, font=('Arial', 9))
        original_text.insert(1.0, suggestion.original_text)
        original_text.config(state='disabled', bg="#ffebee")
        original_text.pack(fill=tk.X, pady=(0, 5))
        
        # Suggested text
        ttk.Label(suggestion_frame, text="Suggested:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        suggested_text = tk.Text(suggestion_frame, height=3, wrap=tk.WORD, font=('Arial', 9))
        suggested_text.insert(1.0, suggestion.suggested_text)
        suggested_text.config(state='disabled', bg="#e8f5e8")
        suggested_text.pack(fill=tk.X, pady=(0, 5))
        
        # Keywords added
        if suggestion.keywords:
            keywords_text = ", ".join(suggestion.keywords)
            ttk.Label(suggestion_frame, text=f"Keywords added: {keywords_text}", 
                     font=('Arial', 9), foreground="#1565c0").pack(anchor=tk.W)
    
    def update_keywords_view(self):
        """Update the keywords analysis tab"""
        # Job keywords
        self.job_keywords_text.config(state='normal')
        self.job_keywords_text.delete(1.0, tk.END)
        
        job_keywords_text = "Job Requirements Keywords:\n\n"
        for i, keyword in enumerate(self.job_keywords, 1):
            job_keywords_text += f"{i}. {keyword}\n"
        
        self.job_keywords_text.insert(1.0, job_keywords_text)
        self.job_keywords_text.config(state='disabled')
        
        # Resume keywords (extract from current content)
        self.resume_keywords_text.config(state='normal')
        self.resume_keywords_text.delete(1.0, tk.END)
        
        resume_content = self.user_resume.get("content", "")
        resume_keywords = self.extract_keywords_from_text(resume_content)
        
        resume_keywords_text = "Resume Keywords Found:\n\n"
        for i, keyword in enumerate(resume_keywords, 1):
            resume_keywords_text += f"{i}. {keyword}\n"
        
        self.resume_keywords_text.insert(1.0, resume_keywords_text)
        self.resume_keywords_text.config(state='disabled')
        
        # Update statistics
        matching_keywords = set(self.job_keywords) & set(resume_keywords)
        match_percentage = (len(matching_keywords) / len(self.job_keywords)) * 100 if self.job_keywords else 0
        
        stats_text = f"Keyword Match: {len(matching_keywords)}/{len(self.job_keywords)} ({match_percentage:.1f}%)"
        self.keyword_stats_label.config(text=stats_text)
    
    def extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords from text (simplified implementation)"""
        # This is a simplified version - in practice, you'd use more sophisticated NLP
        words = re.findall(r'\b[A-Za-z]{3,}\b', text.lower())
        
        # Filter for technical terms and skills
        technical_terms = []
        for word in words:
            if any(tech in word for tech in ['python', 'java', 'react', 'sql', 'aws', 'docker', 'git']):
                technical_terms.append(word)
        
        return list(set(technical_terms))
    
    def update_preview(self):
        """Update the final preview"""
        self.preview_text.config(state='normal')
        self.preview_text.delete(1.0, tk.END)
        
        preview_content = self.user_resume.get("content", "")
        self.preview_text.insert(1.0, preview_content)
        self.preview_text.config(state='disabled')
    
    def update_footer(self):
        """Update the footer with current statistics"""
        # Calculate ATS score (simplified)
        ats_score = self.calculate_ats_score()
        self.ats_score_label.config(text=f"ATS Score: {ats_score:.1f}/100")
        
        # Count changes
        changes_count = len([s for s in self.optimization_suggestions if s.approved])
        self.changes_label.config(text=f"Changes: {changes_count} modifications")
    
    def calculate_ats_score(self) -> float:
        """Calculate ATS compatibility score"""
        # Simplified ATS scoring
        score = 0.0
        
        # Keyword matching (40% of score)
        resume_content = self.user_resume.get("content", "").lower()
        keyword_matches = sum(1 for keyword in self.job_keywords if keyword.lower() in resume_content)
        keyword_score = (keyword_matches / len(self.job_keywords)) * 40 if self.job_keywords else 0
        score += keyword_score
        
        # Content length (20% of score)
        content_length = len(resume_content.split())
        if 300 <= content_length <= 800:
            score += 20
        elif content_length > 200:
            score += 10
        
        # Structure (20% of score)
        if "experience" in resume_content and "education" in resume_content:
            score += 20
        
        # Technical skills (20% of score)
        technical_keywords = ['python', 'java', 'javascript', 'sql', 'aws', 'docker', 'git']
        tech_matches = sum(1 for tech in technical_keywords if tech in resume_content)
        score += min(tech_matches * 3, 20)
        
        return min(score, 100)
    
    def on_text_change(self, event=None):
        """Handle text changes in the optimized text area"""
        # Update user resume content
        self.user_resume["content"] = self.optimized_text.get(1.0, tk.END + "-1c")
        
        # Update other tabs
        self.update_keywords_view()
        self.update_preview()
        self.update_footer()
    
    def on_suggestion_toggle(self, index: int):
        """Handle suggestion checkbox toggle"""
        var = self.suggestion_vars.get(f"suggestion_{index}")
        if var and index < len(self.optimization_suggestions):
            self.optimization_suggestions[index].approved = var.get()
            
            # Apply or remove the suggestion
            if var.get():
                self.apply_suggestion(index)
            else:
                self.remove_suggestion(index)
    
    def apply_suggestion(self, index: int):
        """Apply a specific suggestion"""
        suggestion = self.optimization_suggestions[index]
        current_content = self.user_resume.get("content", "")
        
        # Replace original text with suggested text
        updated_content = current_content.replace(suggestion.original_text, suggestion.suggested_text)
        self.user_resume["content"] = updated_content
        
        # Update the optimized text widget
        self.optimized_text.delete(1.0, tk.END)
        self.optimized_text.insert(1.0, updated_content)
        
        # Update other views
        self.update_keywords_view()
        self.update_preview()
        self.update_footer()
    
    def remove_suggestion(self, index: int):
        """Remove a specific suggestion"""
        suggestion = self.optimization_suggestions[index]
        current_content = self.user_resume.get("content", "")
        
        # Replace suggested text back with original text
        updated_content = current_content.replace(suggestion.suggested_text, suggestion.original_text)
        self.user_resume["content"] = updated_content
        
        # Update the optimized text widget
        self.optimized_text.delete(1.0, tk.END)
        self.optimized_text.insert(1.0, updated_content)
        
        # Update other views
        self.update_keywords_view()
        self.update_preview()
        self.update_footer()
    
    def apply_selected_suggestions(self):
        """Apply all selected suggestions"""
        applied_count = 0
        for i, suggestion in enumerate(self.optimization_suggestions):
            if suggestion.approved:
                self.apply_suggestion(i)
                applied_count += 1
        
        messagebox.showinfo("Suggestions Applied", 
                           f"Applied {applied_count} optimization suggestions.")
    
    def revert_all_changes(self):
        """Revert all changes to original resume"""
        if messagebox.askyesno("Revert Changes", 
                              "Are you sure you want to revert all changes to the original resume?"):
            self.user_resume["content"] = self.original_resume.get("content", "")
            
            # Uncheck all suggestions
            for var in self.suggestion_vars.values():
                var.set(False)
            
            for suggestion in self.optimization_suggestions:
                suggestion.approved = False
            
            # Update interface
            self.update_interface()
    
    def export_to_word(self):
        """Export the current resume to a Word document"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word documents", "*.docx"), ("All files", "*.*")],
            title="Export Resume"
        )
        
        if filename:
            try:
                # This would require python-docx library
                # For now, save as text file
                with open(filename.replace('.docx', '.txt'), 'w', encoding='utf-8') as f:
                    f.write(self.user_resume.get("content", ""))
                
                messagebox.showinfo("Export Successful", f"Resume exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Failed to export resume: {e}")
    
    def cancel_editing(self):
        """Cancel editing and close the editor"""
        if messagebox.askyesno("Cancel Editing", 
                              "Are you sure you want to cancel? All changes will be lost."):
            self.hide()
            if self.on_reject_callback:
                self.on_reject_callback()
    
    def save_and_continue(self):
        """Save changes and continue with automation"""
        # Validate the resume
        if not self.user_resume.get("content", "").strip():
            messagebox.showerror("Invalid Resume", "Resume content cannot be empty.")
            return
        
        # Calculate final score
        final_score = self.calculate_ats_score()
        
        # Confirm save
        if messagebox.askyesno("Save Resume", 
                              f"Save optimized resume with ATS score {final_score:.1f}/100 and continue with application?"):
            self.hide()
            if self.on_save_callback:
                self.on_save_callback(self.user_resume["content"], final_score)
    
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def show(self):
        """Show the editor window"""
        if not self.window:
            self.create_window()
        
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        self.visible = True
    
    def hide(self):
        """Hide the editor window"""
        if self.window:
            self.window.withdraw()
        self.visible = False
    
    def on_window_close(self):
        """Handle window close event"""
        self.cancel_editing()

if __name__ == "__main__":
    # Test the editor
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    editor = InteractiveResumeEditor()
    editor.show()
    
    # Test data
    original = "John Doe\nSoftware Developer\nExperience with Python and web development."
    optimized = "John Doe\nSenior Software Developer\nExtensive experience with Python, Django, React, and modern web development technologies including AWS cloud services."
    
    suggestions = [
        {
            "section": "Professional Summary",
            "original_text": "Software Developer",
            "suggested_text": "Senior Software Developer",
            "keywords": ["Senior"],
            "reason": "Match job seniority level"
        },
        {
            "section": "Technical Skills",
            "original_text": "Python and web development",
            "suggested_text": "Python, Django, React, and modern web development technologies including AWS cloud services",
            "keywords": ["Django", "React", "AWS"],
            "reason": "Add job-specific technical requirements"
        }
    ]
    
    editor.load_resume_data(original, optimized, "Senior Python Developer", "Tech Corp", 
                           ["Python", "Django", "React", "AWS"], 85.5, suggestions)
    
    root.mainloop()
