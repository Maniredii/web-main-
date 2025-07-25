#!/usr/bin/env python3
"""
Reliable popup system that ALWAYS works
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
import os
import sys

class ReliablePopup:
    def __init__(self):
        self.user_confirmed = False
        self.popup_active = False
    
    def show_popup(self, title, message, instructions=""):
        """Show popup with multiple fallback methods"""
        print(f"\n🚨 MANUAL INTERVENTION REQUIRED: {title}")
        print("=" * 60)
        print(f"📋 {message}")
        if instructions:
            print(f"💡 {instructions}")
        print("=" * 60)
        
        # Try multiple methods in order of reliability
        methods = [
            self._method_1_simple_messagebox,
            self._method_2_custom_popup,
            self._method_3_separate_process,
            self._method_4_terminal_fallback
        ]
        
        for i, method in enumerate(methods, 1):
            try:
                print(f"🔄 Trying popup method {i}...")
                if method(title, message, instructions):
                    print("✅ User confirmed via popup!")
                    return True
            except Exception as e:
                print(f"⚠️ Method {i} failed: {e}")
                continue
        
        print("❌ All popup methods failed")
        return False
    
    def _method_1_simple_messagebox(self, title, message, instructions=""):
        """Simplest method - basic messagebox"""
        try:
            # Create a new root for this popup
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            root.lift()
            root.focus_force()
            
            # Combine message and instructions
            full_message = f"{message}\n\n{instructions}" if instructions else message
            
            # Show messagebox
            result = messagebox.showinfo(
                "🚨 LinkedIn Automation - Manual Action Required",
                full_message
            )
            
            root.destroy()
            return True
            
        except Exception as e:
            print(f"Messagebox failed: {e}")
            return False
    
    def _method_2_custom_popup(self, title, message, instructions=""):
        """Custom popup window"""
        try:
            self.user_confirmed = False
            
            # Create root
            root = tk.Tk()
            root.withdraw()
            
            # Create popup
            popup = tk.Toplevel()
            popup.title("LinkedIn Automation - Manual Action Required")
            popup.geometry("450x300")
            popup.resizable(False, False)
            popup.configure(bg='white')
            
            # Make it prominent
            popup.attributes('-topmost', True)
            popup.grab_set()
            popup.lift()
            popup.focus_force()
            
            # Prevent closing
            popup.protocol("WM_DELETE_WINDOW", lambda: None)
            
            # Header
            header = tk.Frame(popup, bg='#d32f2f', height=60)
            header.pack(fill='x')
            header.pack_propagate(False)
            
            title_label = tk.Label(header, text=title, 
                                  font=('Arial', 14, 'bold'),
                                  bg='#d32f2f', fg='white')
            title_label.pack(expand=True)
            
            # Content
            content = tk.Frame(popup, bg='white')
            content.pack(fill='both', expand=True, padx=30, pady=20)
            
            # Message
            msg_label = tk.Label(content, text=message,
                                font=('Arial', 12),
                                bg='white', fg='black',
                                wraplength=380, justify='center')
            msg_label.pack(pady=(0, 15))
            
            # Instructions
            if instructions:
                inst_label = tk.Label(content, text=instructions,
                                     font=('Arial', 10),
                                     bg='white', fg='#666',
                                     wraplength=380, justify='center')
                inst_label.pack(pady=(0, 20))
            
            # Button
            def on_continue():
                self.user_confirmed = True
                popup.destroy()
                root.quit()
            
            btn = tk.Button(content, text="✅ CONTINUE AUTOMATION",
                           command=on_continue,
                           font=('Arial', 12, 'bold'),
                           bg='#4CAF50', fg='white',
                           padx=40, pady=15,
                           relief='flat')
            btn.pack(pady=20)
            
            # Center on screen
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() - 450) // 2
            y = (popup.winfo_screenheight() - 300) // 2
            popup.geometry(f"450x300+{x}+{y}")
            
            # Flash for attention
            def flash():
                for _ in range(5):
                    popup.configure(bg='yellow')
                    popup.update()
                    time.sleep(0.1)
                    popup.configure(bg='white')
                    popup.update()
                    time.sleep(0.1)
            
            popup.after(100, flash)
            
            # Focus on button
            btn.focus_set()
            
            # Run popup
            popup.mainloop()
            
            # Cleanup
            try:
                root.destroy()
            except:
                pass
            
            return self.user_confirmed
            
        except Exception as e:
            print(f"Custom popup failed: {e}")
            return False
    
    def _method_3_separate_process(self, title, message, instructions=""):
        """Run popup in separate process"""
        try:
            import subprocess
            
            popup_code = f'''
import tkinter as tk
from tkinter import messagebox
import sys

try:
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    message = """{message}"""
    instructions = """{instructions}"""
    full_message = message + "\\n\\n" + instructions if instructions else message
    
    messagebox.showinfo("🚨 Manual Action Required", full_message)
    root.destroy()
    sys.exit(0)
    
except Exception as e:
    print(f"Error: {{e}}")
    sys.exit(1)
'''
            
            with open('temp_popup.py', 'w') as f:
                f.write(popup_code)
            
            result = subprocess.run([sys.executable, 'temp_popup.py'], 
                                  timeout=300, capture_output=True)
            
            try:
                os.remove('temp_popup.py')
            except:
                pass
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Subprocess popup failed: {e}")
            return False
    
    def _method_4_terminal_fallback(self, title, message, instructions=""):
        """Terminal fallback - always works"""
        print("\n" + "🔴" * 30)
        print("🚨 POPUP FAILED - USING TERMINAL")
        print("🔴" * 30)
        print(f"📋 {message}")
        if instructions:
            print(f"💡 {instructions}")
        print("🔴" * 30)
        print("⌨️ Press ENTER after completing the action...")
        print("🔴" * 30)
        
        try:
            input()
            return True
        except:
            return False

# Test the popup system
def test_popup():
    popup = ReliablePopup()
    
    print("🧪 Testing Reliable Popup System...")
    
    result = popup.show_popup(
        "🤖 CAPTCHA Detected",
        "LinkedIn is asking you to complete a CAPTCHA puzzle.\n\nPlease solve the CAPTCHA in the browser window.",
        "Click the button after completing the CAPTCHA to continue automation"
    )
    
    if result:
        print("✅ Popup test successful!")
    else:
        print("❌ Popup test failed!")
    
    return result

if __name__ == '__main__':
    test_popup()
