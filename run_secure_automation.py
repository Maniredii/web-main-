#!/usr/bin/env python3
"""
🔒 Secure LinkedIn Automation Runner
Enhanced version with comprehensive anti-detection measures
"""

import logging
import sys
import time
from linkedin_ollama_automation import LinkedInOllamaAutomation, AutomationStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation_security.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Run the enhanced LinkedIn automation with security features"""
    
    print("🔒 LinkedIn Automation - Enhanced Security Mode")
    print("=" * 50)
    print("🛡️  Anti-detection features enabled:")
    print("   • Stealth browser configuration")
    print("   • Human behavior simulation")
    print("   • Random delays and timing")
    print("   • User agent rotation")
    print("   • Security challenge handling")
    print("   • 2FA support")
    print("   • Human-like typing")
    print("   • Mouse movement simulation")
    print("=" * 50)
    
    try:
        # Initialize automation with conservative strategy for maximum safety
        automation = LinkedInOllamaAutomation(
            profile_path="my_details.json",
            strategy=AutomationStrategy.CONSERVATIVE
        )
        
        print("\n🚀 Starting secure automation...")
        print("⚠️  Important security notes:")
        print("   • Keep your account activity normal")
        print("   • Complete any security challenges manually")
        print("   • Monitor for any LinkedIn warnings")
        print("   • Don't exceed 10-15 applications per day")
        
        # Add a safety delay before starting
        print("\n⏳ Adding safety delay before starting...")
        time.sleep(5)
        
        # Run the automation
        automation.run_automation()
        
    except KeyboardInterrupt:
        print("\n⚠️  Automation interrupted by user")
        logger.info("Automation stopped by user")
    except Exception as e:
        print(f"\n❌ Automation error: {e}")
        logger.error(f"Automation failed: {e}")
        return False
    
    print("\n✅ Automation completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 Check the logs for detailed information:")
        print("   • automation_security.log - Detailed logs")
        print("   • job_applications_*.json - Application results")
    else:
        print("\n❌ Automation failed. Check logs for details.")
        sys.exit(1) 