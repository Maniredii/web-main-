# Auto Job Applier - AI-Powered Job Application Tool

A comprehensive desktop application that automates job applications using AI-powered analysis, resume parsing, and intelligent job matching.

## 🚀 Features

### Core Functionality
- **Resume Parsing**: Supports DOCX, PDF, and TXT formats
- **AI-Powered Job Analysis**: Uses Ollama (Llama 3) for intelligent job compatibility scoring
- **Multi-Platform Job Search**: Search jobs on Indeed, LinkedIn, and Glassdoor
- **Browser Automation**: Opens selected job platform in browser with search results
- **Glassdoor Integration**: Automatic login with provided credentials
- **Automatic Cover Letter Generation**: AI-generated personalized cover letters
- **Smart Application Filtering**: Only applies to high-compatibility jobs
- **Real-time Logging**: Live application status and progress tracking

### Technical Features
- **Tkinter GUI**: Modern, user-friendly desktop interface
- **Threading**: Non-blocking operations for smooth user experience
- **Modular Architecture**: Clean, maintainable code structure
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Standalone Executable**: Can be packaged as a single .exe file

## 📋 Prerequisites

### Required Software
1. **Python 3.10+** (3.11+ recommended)
2. **Ollama** - Local LLM server
3. **Chrome Browser** (for web automation)

### Ollama Setup
```bash
# Install Ollama from https://ollama.ai
# Pull the recommended model
ollama pull llama3:latest
# Start Ollama server
ollama serve
```

## 🛠️ Installation

### Option 1: Run from Source
```bash
# Clone or download the project
cd web-ui-main

# Install dependencies
pip install -r requirements.txt

# Run the application
python auto_job_applier.py
```

### Option 2: Build Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
python build_exe.py

# The executable will be created in dist/AutoJobApplier.exe
```

## 🎯 Usage Guide

### 1. Launch the Application
- Run `python auto_job_applier.py` or double-click `AutoJobApplier.exe`
- The application will check Ollama availability on startup

### 2. Load Your Resume
- Click "Browse" to select your resume file
- Supported formats: DOCX, PDF, TXT
- Click "Load Resume" to parse and extract information
- View extracted skills in the logs

### 3. Configure Job Search
- **Keywords**: Enter job search terms (e.g., "python developer", "data scientist")
- **Location**: Specify location (e.g., "remote", "New York", "London")
- **Job Site**: Select platform (Indeed, LinkedIn, Glassdoor)

### 4. Search for Jobs
- Click "Search Jobs" to open the selected platform in your browser
- The application will automatically navigate to the job search page
- For Glassdoor, it will automatically log in using the provided credentials
- Use "Close Browser" to close the browser window when done
- Jobs will appear in the center panel
- Select a job to analyze

### 5. Analyze Jobs
- Select a job from the list
- Click "Analyze Job" for AI-powered compatibility analysis
- View detailed analysis including:
  - Compatibility score (0-100)
  - Skills match/missing skills
  - Recommendations
  - Should apply decision

### 6. Generate Cover Letters
- Select a job and click "Generate Cover Letter"
- AI creates personalized cover letters
- Copy and customize as needed

### 7. Auto Apply
- Click "Start Auto Apply" to begin automated applications
- Application only applies to high-compatibility jobs (70%+ score)
- Monitor progress in real-time logs
- Click "Stop" to halt the process

## 🔧 Configuration

### Application Settings
The application uses several configuration files:

- `config.json`: General application settings
- `my_details.json`: User profile information
- `auto_job_applier.log`: Application logs

### Ollama Configuration
- **Endpoint**: `http://localhost:11434` (default)
- **Model**: `llama3:latest` (recommended)
- **Customization**: Modify in `auto_job_applier.py` OllamaManager class

## 📁 Project Structure

```
web-ui-main/
├── auto_job_applier.py          # Main application
├── build_exe.py                 # Build script for executable
├── requirements.txt             # Python dependencies
├── config.json                  # Application configuration
├── my_details.json              # User profile
├── AUTO_JOB_APPLIER_README.md   # This file
├── dist/                        # Built executable (after build)
│   └── AutoJobApplier.exe
└── templates/                   # Web dashboard templates (legacy)
```

## 🏗️ Building the Executable

### Automated Build
```bash
python build_exe.py
```

### Manual Build
```bash
pyinstaller --onefile --windowed --name=AutoJobApplier auto_job_applier.py
```

### Build Options
- `--onefile`: Single executable file
- `--windowed`: No console window
- `--icon=icon.ico`: Custom icon (optional)
- `--add-data`: Include additional files

## 🔍 Troubleshooting

### Common Issues

#### Ollama Not Available
```
⚠️ Ollama is not available. Install Ollama and run: ollama pull llama3:latest
```
**Solution**: 
1. Install Ollama from https://ollama.ai
2. Run `ollama pull llama3:latest`
3. Start Ollama with `ollama serve`

#### Resume Parsing Errors
```
❌ Failed to load resume: [Error details]
```
**Solutions**:
- Ensure file is not corrupted
- Try different file format (DOCX preferred)
- Check file permissions

#### Job Search Issues
```
❌ Search error: [Error details]
```
**Solutions**:
- Check internet connection
- Verify job site is accessible
- Try different keywords/location

#### Build Errors
```
❌ Build failed: [Error details]
```
**Solutions**:
- Update PyInstaller: `pip install --upgrade pyinstaller`
- Install missing dependencies
- Run as administrator (Windows)

### Performance Tips
- Use SSD storage for faster file operations
- Close unnecessary applications during auto-apply
- Monitor system resources during long operations

## 🔒 Security & Privacy

### Data Handling
- Resume data is processed locally
- No personal data is sent to external servers
- Ollama runs locally on your machine
- Job descriptions are fetched from public job sites

### Best Practices
- Keep Ollama updated
- Use strong passwords for job site accounts
- Monitor application logs for suspicious activity
- Regularly backup your configuration files

## 🚀 Advanced Features

### Custom Job Sites
Add support for additional job sites by extending the `JobScraper` class:

```python
def _search_custom_site(self, keywords: str, location: str) -> List[Dict[str, Any]]:
    # Implement custom job site scraping
    pass
```

### Custom AI Prompts
Modify AI analysis prompts in the `OllamaManager` class:

```python
def analyze_job_compatibility(self, job_description: str, resume_text: str):
    # Customize the analysis prompt
    prompt = f"""
    Your custom analysis prompt here...
    """
```

### Integration with Existing Systems
- Export job analysis results to CSV/Excel
- Integrate with ATS systems
- Connect to CRM for application tracking

## 📊 Performance Metrics

### Typical Performance
- **Resume Parsing**: 1-3 seconds
- **Job Search**: 5-15 seconds (depends on site)
- **AI Analysis**: 10-30 seconds (depends on Ollama model)
- **Cover Letter Generation**: 15-45 seconds
- **Auto Apply**: 30-60 seconds per job

### Resource Usage
- **Memory**: 100-300 MB
- **CPU**: Low during idle, moderate during AI operations
- **Network**: Minimal (job scraping and Ollama queries)

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Add type hints
- Include docstrings
- Write unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Getting Help
1. Check the troubleshooting section
2. Review application logs
3. Search existing issues
4. Create a new issue with detailed information

### Feature Requests
- Use the issue tracker
- Provide detailed use case descriptions
- Include mockups or examples

---

**Note**: This application is for educational and personal use. Always comply with job site terms of service and respect rate limits. Use responsibly and ethically. 