# 🚀 LinkedIn Job Application Automation

**AI-Powered LinkedIn Job Application Automation with Ollama Integration**

Automate your LinkedIn job applications with intelligent AI assistance, comprehensive profile management, and smart job matching.

## ⚡ Quick Start (2 Steps)

**New users start here:**

```bash
# 1. Set up your details (one-time setup)
python setup_my_details.py

# 2. Run the automation
python linkedin_ollama_automation.py
```

**That's it!** The automation will automatically use your details for job applications.

## 🎯 Key Features

### 🤖 **AI-Powered Automation**
- **Ollama Integration**: Local AI for intelligent form filling
- **Smart Job Matching**: AI analyzes job compatibility
- **Adaptive Strategy**: Learns from application success rates
- **Computer Vision**: Handles complex form elements

### 📋 **Profile Management**
- **Simple Setup**: Easy configuration with `my_details.json` or `my_details.txt`
- **Advanced Profiles**: Full profile manager with GUI/CLI interfaces
- **Template System**: Pre-built templates for different roles
- **Secure Storage**: Optional encryption for sensitive data

### 🎯 **Smart Job Search**
- **Intelligent Filtering**: Filters jobs based on your criteria
- **Application Tracking**: Comprehensive logging and reporting
- **Multi-Site Support**: LinkedIn, Indeed, Glassdoor (planned)
- **Rate Limiting**: Respects platform limits and human-like behavior

## 📦 Installation

### Prerequisites
- **Python 3.8+**
- **Chrome Browser**
- **Ollama** (for AI features)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Install Ollama
```bash
# Download and install Ollama from https://ollama.ai
# Then pull the recommended model:
ollama pull llama3:latest
```

## 🛠️ Setup Options

### Option 1: Simple Setup (Recommended)
```bash
# Interactive setup - easiest for new users
python setup_my_details.py
```

Creates `my_details.json` or `my_details.txt` with your information.

### Option 2: Advanced Profile Manager
```bash
# GUI interface
python profile_manager.py

# CLI interface
python profile_manager.py --cli
```

Full-featured profile management with templates, validation, and encryption.

### Option 3: Manual Configuration
Edit `my_details.json` directly:
```json
{
  "personal_info": {
    "name": "Your Name",
    "email": "your.email@example.com",
    "phone": "+1-555-123-4567",
    "location": "City, State"
  },
  "professional_info": {
    "current_title": "Software Engineer",
    "experience_years": 5,
    "skills": ["Python", "JavaScript", "React"],
    "summary": "Experienced developer..."
  },
  "job_search_preferences": {
    "keywords": ["Python Developer", "Software Engineer"],
    "locations": ["Remote", "San Francisco"],
    "experience_level": "Mid-Senior level",
    "job_types": ["Full-time"],
    "remote_preference": true
  }
}
```

## 🚀 Usage

### Basic Usage
```bash
python linkedin_ollama_automation.py
```

### Advanced Configuration
Edit `config.json` to customize:
- **Ollama Settings**: Model, endpoint, parameters
- **Automation Strategy**: Adaptive, conservative, aggressive
- **LinkedIn Filters**: Date posted, easy apply, remote jobs
- **Application Settings**: Auto-submit, manual review, delays

### Environment Variables
```bash
export LINKEDIN_PASSWORD="your_password"
export OLLAMA_ENDPOINT="http://localhost:11434"
export OLLAMA_MODEL="llama3:latest"
```

## 🔧 Troubleshooting

### Common Issues

**Ollama Connection**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve
```

**LinkedIn Login Issues**
- Verify credentials in environment variables
- Handle 2FA manually when prompted
- Check for security challenges

**Application Failures**
- Review job compatibility scores in logs
- Verify resume/cover letter file paths
- Check form filling logic in debug mode

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and personal use only. Users are responsible for complying with LinkedIn's Terms of Service and applicable laws. Use responsibly and ethically.

---

**Happy Job Hunting! 🎯**
