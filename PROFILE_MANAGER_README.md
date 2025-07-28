# 🔧 LinkedIn Profile Manager

A comprehensive user profile management system for the LinkedIn job application automation. This system provides an intuitive interface for users to input, manage, and validate their personal and professional information for automated job applications.

## 🌟 Features

### 📝 Profile Data Collection
- **Personal Information**: Name, email, phone, location, LinkedIn URL, website
- **Professional Details**: Current title, experience, skills, education, salary expectations
- **Job Search Criteria**: Keywords, location preferences, experience level, remote work preferences
- **Document Management**: Resume, cover letter, and portfolio file paths

### 🔒 Security & Privacy
- **Encryption Support**: Password-based profile encryption using Fernet cryptography
- **Privacy Options**: Exclude sensitive information from automation
- **Secure Storage**: Local encrypted storage with backup functionality

### 🎨 User Interfaces
- **GUI Interface**: User-friendly Tkinter-based graphical interface with tabbed layout
- **CLI Interface**: Command-line interface for headless environments
- **Template System**: Pre-defined templates for different job types

### 🔄 Integration
- **Seamless Integration**: Works with existing LinkedIn automation system
- **Legacy Compatibility**: Maintains backward compatibility with existing profiles
- **Field Mapping**: Intelligent form field mapping for various application forms

## 🚀 Quick Start

### Installation

1. **Install Dependencies**:
```bash
pip install cryptography>=3.4.8
```

2. **Run Profile Manager**:
```bash
# GUI Interface (default)
python profile_manager.py

# CLI Interface
python profile_manager.py --cli
```

### First Time Setup

1. **Create Your Profile**:
   - Launch the profile manager
   - Fill in your personal and professional information
   - Set your job search criteria
   - Add document file paths
   - Save your profile

2. **Validate Your Profile**:
   - Use the "Validate" button to check for errors
   - Fix any validation issues
   - Save the validated profile

3. **Use with Automation**:
   - Your profile is automatically integrated with the LinkedIn automation
   - Run the automation as usual - it will use your profile data

## 📋 Profile Templates

The system includes pre-defined templates for common job types:

- **Software Engineer**: Technical skills, programming languages, development experience
- **Data Scientist**: Analytics skills, machine learning, statistical analysis
- **Product Manager**: Product strategy, stakeholder management, market analysis
- **Marketing Specialist**: Digital marketing, campaign management, analytics

### Using Templates

**GUI**: Go to the "Templates" tab and click "Load [Template Name] Template"

**CLI**: Select option 5 from the main menu and choose a template

## 🔧 Configuration Options

### Security Settings

- **Enable Encryption**: Protect your profile with password-based encryption
- **Privacy Options**: Exclude phone numbers or salary information from automation
- **Backup Management**: Automatic backups with manual backup creation

### Automation Integration

The profile manager automatically creates a `user_profile.json` file that integrates with the LinkedIn automation system. No additional configuration is required.

## 📁 File Structure

```
profiles/                    # Profile storage directory
├── user_profile.json       # Main profile file
├── backups/                # Automatic backups
│   ├── backup_YYYYMMDD_HHMMSS.json
│   └── ...
└── templates/              # Custom templates
    ├── template_custom.json
    └── ...
```

## 🔍 Validation Rules

The system validates:

- **Email Format**: Valid email address format
- **Phone Numbers**: Valid phone number format (US/International)
- **File Paths**: Existence and accessibility of document files
- **Required Fields**: Essential information for job applications
- **Data Consistency**: Logical consistency between related fields

## 🛠️ Advanced Usage

### Custom Templates

1. **Create Profile**: Set up your profile with specific information
2. **Save as Template**: Go to Templates tab → Enter template name → Save Template
3. **Use Template**: Load the custom template for future profiles

### Backup and Export

- **Automatic Backups**: Created every time you save your profile
- **Manual Backups**: Use the "Create Backup" button in Security tab
- **Export Profile**: Save profile to any location for sharing or migration
- **Import Profile**: Load profile from external file

### CLI Commands

```bash
# Create new profile
python profile_manager.py --cli
# Select option 1

# Edit existing profile
python profile_manager.py --cli
# Select option 2

# Validate profile
python profile_manager.py --cli
# Select option 3
```

## 🔗 Integration with Automation

The profile manager seamlessly integrates with `linkedin_ollama_automation.py`:

1. **Automatic Detection**: Automation detects and uses the enhanced profile system
2. **Field Mapping**: Intelligent mapping of profile data to form fields
3. **Fallback Support**: Falls back to legacy system if profile manager is unavailable
4. **Real-time Updates**: Changes to profile are immediately available to automation

### Integration Features

- **Smart Field Recognition**: Automatically fills forms based on field names and labels
- **Multiple Format Support**: Handles various form field naming conventions
- **Error Recovery**: Graceful fallback to manual input if field mapping fails
- **Performance Optimization**: Cached profile data for faster form filling

## 🐛 Troubleshooting

### Common Issues

1. **GUI Not Available**:
   - Automatically falls back to CLI interface
   - Install tkinter if needed: `sudo apt-get install python3-tk` (Linux)

2. **Profile Not Loading**:
   - Check file permissions in profiles directory
   - Verify profile file format (JSON)
   - Use validation to check for errors

3. **Encryption Issues**:
   - Ensure correct password is entered
   - Check that cryptography package is installed
   - Disable encryption if having persistent issues

4. **Integration Problems**:
   - Verify `profile_integration.py` is in the same directory
   - Check that profile file exists and is valid
   - Run validation to ensure profile completeness

### Getting Help

- Check validation messages for specific errors
- Use CLI interface if GUI has issues
- Review log files for detailed error information
- Ensure all required dependencies are installed

## 📈 Future Enhancements

- Web-based interface for remote management
- Multi-profile support for different job types
- Advanced analytics and application tracking
- Integration with additional job platforms
- AI-powered profile optimization suggestions

## 🤝 Contributing

The profile manager is designed to be extensible. Key areas for contribution:

- Additional validation rules
- New profile templates
- Enhanced field mapping
- Additional security features
- UI/UX improvements

---

**Note**: This profile manager is specifically designed for the LinkedIn job application automation system and provides a secure, user-friendly way to manage your professional information for automated job applications.
