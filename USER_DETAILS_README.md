# 📋 User Details System - Simple Job Application Setup

The easiest way to set up your personal information for LinkedIn job applications.

## 🚀 Quick Start (3 Steps)

### Step 1: Setup Your Details
```bash
python setup_my_details.py
```
This interactive script will:
- Ask for your personal information
- Create a configuration file with your details
- Test that everything is working

### Step 2: Review Your Configuration
Your details are saved in either:
- `my_details.json` (structured format)
- `my_details.txt` (simple text format)

You can edit these files anytime to update your information.

### Step 3: Run LinkedIn Automation
```bash
python linkedin_ollama_automation.py
```
The automation will automatically use your details for job applications!

## 📄 What Information Do You Need?

### Required Information:
- ✅ **Full Name** - Your complete name
- ✅ **Email Address** - For job applications

### Optional (but recommended):
- 📱 **Phone Number** - With country code (e.g., +1-555-123-4567)
- 📍 **Location** - City, State, Country
- 🔗 **LinkedIn URL** - Your LinkedIn profile
- 🌐 **Website** - Personal website or portfolio
- 💼 **Current Job Title** - Your current position
- ⏱️ **Years of Experience** - Number of years
- 🎓 **Education** - Highest degree and school
- 📝 **Professional Summary** - Brief description of yourself
- 🛠️ **Skills** - List of your key skills
- 🎯 **Desired Job Titles** - What roles you're looking for

## 📁 File Formats

### JSON Format (`my_details.json`)
```json
{
  "personal_info": {
    "name": "John Smith",
    "email": "john.smith@email.com",
    "phone": "+1-555-123-4567",
    "location": "San Francisco, CA, USA",
    "linkedin_url": "https://linkedin.com/in/johnsmith",
    "website": "https://johnsmith.dev"
  },
  "professional_info": {
    "current_title": "Software Engineer",
    "experience_years": 5,
    "skills": ["Python", "JavaScript", "React"],
    "summary": "Experienced software engineer..."
  }
}
```

### Text Format (`my_details.txt`)
```
FULL_NAME: John Smith
EMAIL: john.smith@email.com
PHONE: +1-555-123-4567
LOCATION: San Francisco, CA, USA
LINKEDIN: https://linkedin.com/in/johnsmith
WEBSITE: https://johnsmith.dev

CURRENT_JOB_TITLE: Software Engineer
YEARS_OF_EXPERIENCE: 5
SKILLS:
Python
JavaScript
React
```

## 🔧 Manual Setup

If you prefer to create the files manually:

1. **Copy a template file:**
   - Copy `my_details.json` or `my_details.txt`
   - Or create your own using the examples above

2. **Fill in your information:**
   - Replace placeholder text with your actual details
   - Required: name and email
   - Optional: everything else (but recommended)

3. **Save the file:**
   - Keep the filename as `my_details.json` or `my_details.txt`
   - The automation will automatically find and use it

## ✅ Validation

The system automatically validates:
- ✅ **Email Format** - Must contain @ and domain
- ✅ **Phone Numbers** - Checks for proper format
- ✅ **URLs** - Validates LinkedIn and website URLs
- ✅ **Required Fields** - Ensures name and email are provided

## 🔄 How It Works

1. **Automatic Detection** - The automation finds your details file
2. **Smart Field Mapping** - Maps your information to job application forms
3. **Form Filling** - Automatically fills out application forms
4. **Validation** - Ensures data is correct before submitting

## 🛠️ Advanced Features

### Multiple File Support
The system looks for files in this order:
1. `my_details.json`
2. `my_details.txt`
3. `user_details.json`
4. `user_details.txt`

### Field Mapping
Your information is automatically mapped to common form fields:
- **Name** → First Name, Last Name, Full Name
- **Email** → Email Address, Contact Email
- **Phone** → Phone Number, Mobile, Telephone
- **Location** → City, Address, Location
- **LinkedIn** → LinkedIn Profile, LinkedIn URL
- **Website** → Personal Website, Portfolio URL

### Job Search Preferences
Configure your job search settings:
- **Desired Roles** - Job titles you're interested in
- **Preferred Locations** - Where you want to work
- **Work Type** - Full-time, Part-time, Contract
- **Remote Preference** - Remote, Hybrid, On-site
- **Salary Expectations** - Minimum and preferred salary

## 🔒 Security

- **Local Storage** - Your details are stored locally on your computer
- **No Cloud Upload** - Information never leaves your machine
- **File Permissions** - Keep your details files secure
- **Privacy** - Only you have access to your information

## 🆘 Troubleshooting

### "Details file not found"
- Run `python setup_my_details.py` to create the file
- Or manually create `my_details.json` or `my_details.txt`

### "Configuration not complete"
- Make sure you have at least name and email filled in
- Check that values don't start with placeholder text like "YOUR NAME"

### "Validation errors"
- Check email format (must contain @ and domain)
- Verify phone number format (include country code)
- Ensure URLs start with http:// or https://

### Test Your Configuration
```bash
python user_details_loader.py
```
This will test your configuration and show a summary.

## 📝 Examples

### Software Engineer Example
```json
{
  "personal_info": {
    "name": "Sarah Johnson",
    "email": "sarah.johnson@gmail.com",
    "phone": "+1-555-987-6543",
    "location": "Seattle, WA, USA",
    "linkedin_url": "https://linkedin.com/in/sarahjohnson",
    "website": "https://sarahjohnson.dev"
  },
  "professional_info": {
    "current_title": "Senior Software Engineer",
    "experience_years": 7,
    "skills": ["Python", "JavaScript", "React", "AWS", "Docker"],
    "summary": "Experienced full-stack engineer with 7+ years building scalable web applications"
  },
  "job_search_preferences": {
    "desired_roles": ["Senior Software Engineer", "Lead Developer", "Engineering Manager"],
    "work_type": "Full-time",
    "remote_preference": "Hybrid"
  }
}
```

### Marketing Professional Example
```
FULL_NAME: Michael Chen
EMAIL: michael.chen@email.com
PHONE: +1-555-456-7890
LOCATION: Austin, TX, USA
LINKEDIN: https://linkedin.com/in/michaelchen
WEBSITE: https://michaelchen.marketing

CURRENT_JOB_TITLE: Digital Marketing Manager
YEARS_OF_EXPERIENCE: 4
SKILLS:
SEO
Google Ads
Social Media Marketing
Content Strategy
Analytics

DESIRED_ROLES:
Senior Marketing Manager
Marketing Director
Growth Marketing Manager
```

## 🎯 Benefits

- ✅ **Simple Setup** - One-time configuration
- ✅ **Automatic Form Filling** - No manual data entry
- ✅ **Consistent Information** - Same details across all applications
- ✅ **Easy Updates** - Edit files to update information
- ✅ **Multiple Formats** - Choose JSON or text format
- ✅ **Validation** - Catches errors before applying
- ✅ **Privacy** - All data stays on your computer

## 🔄 Integration

This system integrates seamlessly with:
- **LinkedIn Automation** - Automatic form filling
- **Profile Manager** - Enhanced profile system (if available)
- **Job Application Forms** - Smart field mapping
- **Validation System** - Data quality checks

Your details are automatically used by the LinkedIn automation system, making job applications faster and more consistent.

---

**Need Help?** Run `python setup_my_details.py` for interactive setup or check the troubleshooting section above.
