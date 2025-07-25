#!/usr/bin/env python3
"""
Test the manual intervention popup system
"""

import tkinter as tk
from tkinter import messagebox
import time

def test_popup():
    """Test the popup system"""
    print("🧪 Testing Manual Intervention Popup System...")
    
    # Initialize tkinter
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    user_confirmed = False
    
    def show_test_popup(title, message, instructions=""):
        """Show test popup dialog"""
        nonlocal user_confirmed
        user_confirmed = False
        
        def on_confirm():
            nonlocal user_confirmed
            user_confirmed = True
            popup.destroy()
        
        # Create popup window
        popup = tk.Toplevel(root)
        popup.title(title)
        popup.geometry("500x300")
        popup.resizable(False, False)
        
        # Center the popup
        popup.transient(root)
        popup.grab_set()
        
        # Configure popup
        popup.configure(bg='#f0f0f0')
        
        # Title label
        title_label = tk.Label(popup, text=title, font=('Arial', 14, 'bold'), 
                              bg='#f0f0f0', fg='#d32f2f')
        title_label.pack(pady=20)
        
        # Message label
        message_label = tk.Label(popup, text=message, font=('Arial', 11), 
                                bg='#f0f0f0', wraplength=450, justify='center')
        message_label.pack(pady=10)
        
        # Instructions label (if provided)
        if instructions:
            instructions_label = tk.Label(popup, text=instructions, font=('Arial', 9), 
                                        bg='#f0f0f0', fg='#666666', wraplength=450, justify='center')
            instructions_label.pack(pady=5)
        
        # Continue button
        continue_btn = tk.Button(popup, text="✅ Continue Automation", 
                               command=on_confirm, font=('Arial', 11, 'bold'),
                               bg='#4caf50', fg='white', padx=20, pady=10)
        continue_btn.pack(pady=20)
        
        # Center the popup on screen
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        
        # Make popup stay on top
        popup.attributes('-topmost', True)
        popup.focus_force()
        
        print(f"🔔 {title}: {message}")
        
        # Wait for user confirmation
        while not user_confirmed:
            popup.update()
            time.sleep(0.1)
        
        print("✅ User confirmed - continuing...")
    
    # Test different types of popups
    test_scenarios = [
        {
            'title': '🤖 CAPTCHA Detected',
            'message': 'LinkedIn is asking you to complete a CAPTCHA puzzle.\n\nPlease solve the CAPTCHA in the browser window.',
            'instructions': 'Click "Continue Automation" after completing the CAPTCHA'
        },
        {
            'title': '🔒 Security Challenge',
            'message': 'LinkedIn has detected unusual activity and requires verification.\n\nPlease complete the security challenge in the browser.',
            'instructions': 'Follow LinkedIn\'s instructions, then click "Continue Automation"'
        },
        {
            'title': '📱 Two-Factor Authentication',
            'message': 'LinkedIn is requesting two-factor authentication.\n\nPlease enter your verification code in the browser.',
            'instructions': 'Check your phone/email for the code, enter it, then click "Continue Automation"'
        }
    ]
    
    print("🚀 Testing popup scenarios...")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Test {i}/{len(test_scenarios)}: {scenario['title']}")
        show_test_popup(scenario['title'], scenario['message'], scenario['instructions'])
        print(f"✅ Test {i} completed successfully!")
        time.sleep(1)
    
    print("\n🎉 All popup tests completed successfully!")
    print("✅ Manual intervention system is working correctly!")
    
    # Clean up
    root.quit()
    root.destroy()

if __name__ == '__main__':
    test_popup()
