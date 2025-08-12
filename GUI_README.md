# 🚀 LinkedIn Job Applier Pro - GUI Edition

A comprehensive desktop application for automating LinkedIn job searches and applications with resume management capabilities.

## ✨ Features

### 📄 Resume Management
- **Upload Resume**: Support for `.docx` files
- **Resume Preview**: View and edit resume content directly in the app
- **Resume Editor**: Built-in text editor for quick resume modifications
- **Save/Export**: Save changes or export to new locations

### 🔍 Job Search Configuration
- **Job Keywords**: Enter specific job titles or skills
- **Location**: Specify job location (remote, city, etc.)
- **Job Type**: Full-time, Part-time, Contract, Internship, Remote
- **Experience Level**: Entry level to Executive

### 🎮 Automation Controls
- **Start Automation**: Begin LinkedIn job search and scraping
- **Pause/Stop**: Control automation flow
- **Reset**: Clear results and reset state
- **Real-time Status**: Monitor progress and current steps

### 📊 Results & Analytics
- **Job Display**: View found jobs with details
- **Export Results**: Save job data to files
- **Statistics**: Track automation performance
- **Clear Results**: Reset results display

### ⚙️ Settings & Configuration
- **Auto-apply**: Enable automatic job applications
- **Max Jobs**: Limit number of jobs to process
- **Action Delays**: Configure timing between actions
- **Settings Persistence**: Save and load configurations

## 🚀 Getting Started

### Prerequisites
1. **Python 3.7+** installed
2. **Node.js** and **npm** for Puppeteer automation
3. **LinkedIn credentials** stored in `user_credentials.json`

### Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements_gui.txt
   ```

2. **Install Node.js dependencies** (automatically handled by the app):
   ```bash
   npm install puppeteer puppeteer-extra puppeteer-extra-plugin-stealth puppeteer-extra-plugin-anonymize-ua random-useragent
   ```

3. **Ensure credentials file exists**:
   ```json
   {
     "linkedin": {
       "email": "your-email@example.com",
       "password": "your-password"
     }
   }
   ```

### Running the Application

```bash
python linkedin_job_applier_gui.py
```

## 📱 GUI Layout

The application is organized into logical sections:

1. **Header**: Application title and description
2. **Resume Management**: Upload, edit, and manage resume files
3. **Job Search Configuration**: Set search parameters
4. **Automation Controls**: Start, stop, and control automation
5. **Status & Progress**: Real-time automation status
6. **Results Display**: View found jobs and details
7. **Settings**: Configure automation behavior

## 🔧 How It Works

### 1. Resume Setup
- Browse and select your `.docx` resume file
- Preview content in the built-in viewer
- Edit directly using the integrated editor
- Save changes back to the file

### 2. Job Search Configuration
- Enter job keywords (e.g., "python developer", "data scientist")
- Specify location preferences
- Choose job type and experience level
- Configure automation settings

### 3. Automation Process
- Click "Start LinkedIn Automation"
- The app opens a browser using Puppeteer
- Automatically logs into LinkedIn using your credentials
- Navigates to jobs section and performs search
- Reads job descriptions and extracts relevant information
- Saves results to `linkedin_jobs.json`

### 4. Results Management
- View all found jobs in the results section
- Export results to text files
- Clear results for new searches
- Track automation statistics

## 🛡️ Security Features

- **Credential Storage**: Secure storage in JSON file
- **Browser Isolation**: Uses incognito mode for automation
- **Session Management**: Handles LinkedIn security checkpoints
- **Anti-Detection**: Advanced browser fingerprinting and stealth

## 🚨 Important Notes

### LinkedIn Security
- **CAPTCHA/Puzzle Solving**: The automation detects security challenges and waits for manual completion
- **Session Management**: Handles LinkedIn's security checkpoints automatically
- **Rate Limiting**: Built-in delays to avoid triggering anti-bot measures

### Resume Handling
- **File Format**: Currently supports `.docx` files only
- **Content Editing**: Changes are saved back to the original file
- **Backup**: Always keep a backup of your original resume

### Automation Limits
- **Job Processing**: Default limit of 10 jobs per run (configurable)
- **Action Delays**: Configurable delays between actions
- **Browser Control**: Full control over automation start/stop

## 🔍 Troubleshooting

### Common Issues

1. **"No resume selected"**
   - Use the Browse button to select a `.docx` resume file

2. **"Automation failed"**
   - Check your LinkedIn credentials in `user_credentials.json`
   - Ensure Node.js and npm are installed
   - Check console output for detailed error messages

3. **"Security checkpoint detected"**
   - This is normal! Complete the puzzle/CAPTCHA manually in the browser
   - The automation will wait and continue automatically

4. **"No jobs found"**
   - Verify your search keywords and location
   - Check if LinkedIn's page structure has changed
   - Try different search terms

### Debug Mode
- Check the console output for detailed logging
- Monitor the status section for real-time updates
- Use the browser window to see what's happening

## 🚀 Advanced Features

### Future Enhancements
- **Multi-platform Support**: Indeed, Glassdoor, etc.
- **AI Resume Optimization**: Using Ollama for resume improvements
- **Cover Letter Generation**: AI-powered personalized cover letters
- **Application Tracking**: Track application status and responses
- **Email Integration**: Send applications via email
- **Analytics Dashboard**: Detailed performance metrics

### Customization
- **Settings Persistence**: All settings are automatically saved
- **Resume Templates**: Built-in resume editing capabilities
- **Export Formats**: Multiple export options for results
- **Theme Support**: Customizable GUI appearance

## 📞 Support

For issues or questions:
1. Check the console output for error details
2. Verify all dependencies are installed
3. Ensure LinkedIn credentials are correct
4. Check if LinkedIn's page structure has changed

## 🔒 Privacy & Security

- **Local Processing**: All data stays on your machine
- **No Cloud Storage**: Resume and job data never leaves your system
- **Secure Credentials**: Stored locally in encrypted format
- **Browser Isolation**: Uses separate browser instance for automation

---

**Note**: This application is for educational and personal use. Always comply with LinkedIn's Terms of Service and respect rate limits when automating job searches.
