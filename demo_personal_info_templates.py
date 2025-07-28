#!/usr/bin/env python3
"""
🎯 Personal Information Templates Demo
Demonstrates the personal information template system
"""

import os
import json
from pathlib import Path
from personal_info_parser import PersonalInfoParser

def demo_template_system():
    """Demonstrate the personal information template system"""
    print("🎯 Personal Information Templates Demo")
    print("=" * 50)
    
    # 1. Show available template files
    print("\n📁 Available Template Files:")
    template_files = [
        'personal_info_template.json',
        'personal_info_template.csv', 
        'personal_info_template.txt'
    ]
    
    for template_file in template_files:
        if os.path.exists(template_file):
            print(f"  ✅ {template_file}")
        else:
            print(f"  ❌ {template_file} (not found)")
    
    # 2. Create sample filled templates
    print("\n📝 Creating Sample Filled Templates:")
    
    # JSON sample
    json_sample = {
        "personal_information": {
            "name": "Alex Johnson",
            "email": "alex.johnson@email.com",
            "phone": "+1-555-234-5678",
            "location": "Austin, TX, USA",
            "linkedin_url": "https://linkedin.com/in/alexjohnson",
            "website": "https://alexjohnson.dev"
        }
    }
    
    with open('demo_sample.json', 'w') as f:
        json.dump(json_sample, f, indent=2)
    print("  ✅ Created demo_sample.json")
    
    # Text sample
    txt_sample = """# Demo Personal Information

NAME: Alex Johnson

EMAIL: alex.johnson@email.com

PHONE: +1-555-234-5678

LOCATION: Austin, TX, USA

LINKEDIN: https://linkedin.com/in/alexjohnson

WEBSITE: https://alexjohnson.dev

ADDITIONAL_URLS:
https://github.com/alexjohnson
https://alexjohnson.medium.com
"""
    
    with open('demo_sample.txt', 'w') as f:
        f.write(txt_sample)
    print("  ✅ Created demo_sample.txt")
    
    # 3. Test parsing
    print("\n🔍 Testing File Parsing:")
    
    test_files = ['demo_sample.json', 'demo_sample.txt']
    
    for test_file in test_files:
        print(f"\n📄 Parsing {test_file}:")
        try:
            personal_info, errors = PersonalInfoParser.parse_file(test_file)
            
            if personal_info:
                print(f"  ✅ Successfully parsed!")
                print(f"     Name: {personal_info.name}")
                print(f"     Email: {personal_info.email}")
                print(f"     Phone: {personal_info.phone}")
                print(f"     Location: {personal_info.location}")
                print(f"     LinkedIn: {personal_info.linkedin_url}")
                print(f"     Website: {personal_info.website}")
                
                if hasattr(personal_info, '_additional_info'):
                    print(f"     Additional Info: {personal_info._additional_info}")
                
                if errors:
                    print(f"  ⚠️ Warnings: {len(errors)}")
                    for error in errors:
                        print(f"     • {error}")
            else:
                print(f"  ❌ Failed to parse")
                for error in errors:
                    print(f"     • {error}")
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    # 4. Show supported formats
    print(f"\n📋 Supported File Formats:")
    formats = PersonalInfoParser.get_supported_formats()
    for fmt in formats:
        print(f"  • {fmt}")
    
    # 5. Integration example
    print(f"\n🔗 Integration with Profile Manager:")
    print(f"  1. GUI: Profile Manager → Personal Info tab → 'Load from File'")
    print(f"  2. CLI: python profile_manager.py --cli → Option 6")
    print(f"  3. Programmatic: PersonalInfoParser.parse_file('your_file.json')")
    
    # 6. Cleanup demo files
    print(f"\n🧹 Cleaning up demo files...")
    demo_files = ['demo_sample.json', 'demo_sample.txt']
    for demo_file in demo_files:
        if os.path.exists(demo_file):
            os.remove(demo_file)
            print(f"  ✅ Removed {demo_file}")
    
    print(f"\n🎉 Demo completed!")
    print(f"\n📖 Next Steps:")
    print(f"  1. Copy a template file (JSON, CSV, or TXT)")
    print(f"  2. Fill in your personal information")
    print(f"  3. Import using Profile Manager GUI or CLI")
    print(f"  4. Use with LinkedIn automation")

def show_template_examples():
    """Show examples of each template format"""
    print("\n📋 Template Format Examples:")
    print("-" * 40)
    
    print("\n1. JSON Format:")
    print("""
{
  "personal_information": {
    "name": "Your Full Name",
    "email": "your.email@example.com",
    "phone": "+1-555-123-4567",
    "location": "City, State, Country",
    "linkedin_url": "https://linkedin.com/in/username",
    "website": "https://yourwebsite.com"
  }
}
""")
    
    print("\n2. Text Format:")
    print("""
NAME: Your Full Name

EMAIL: your.email@example.com

PHONE: +1-555-123-4567

LOCATION: City, State, Country

LINKEDIN: https://linkedin.com/in/username

WEBSITE: https://yourwebsite.com
""")
    
    print("\n3. CSV Format:")
    print("""
Field,Your Information,Example,Description
name,,John Smith,Your full name
email,,john@email.com,Your email address
phone,,+1-555-123-4567,Your phone number
location,,San Francisco CA,Your location
linkedin_url,,https://linkedin.com/in/john,LinkedIn URL
website,,https://johnsmith.dev,Personal website
""")

if __name__ == "__main__":
    try:
        demo_template_system()
        
        # Ask if user wants to see template examples
        show_examples = input("\nWould you like to see template format examples? (y/n): ").lower().startswith('y')
        if show_examples:
            show_template_examples()
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        print("Make sure personal_info_parser.py is available")
