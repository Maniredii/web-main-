# 📄 Personal Information Templates

Enhanced personal information management system for LinkedIn job application automation.

## 🎯 Overview

The Personal Information Template system allows you to prepare your personal details offline in various file formats and then import them into the Profile Manager. This provides flexibility and convenience for managing your job application data.

## 📁 Available Template Formats

### 1. JSON Format (`personal_info_template.json`)
**Best for**: Structured data, easy editing with code editors
```json
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
```

### 2. CSV Format (`personal_info_template.csv`)
**Best for**: Spreadsheet applications, bulk data management
```csv
Field,Your Information,Example,Description
name,,John Smith,Your full name as it appears on your resume
email,,john@email.com,Your primary email address
phone,,+1-555-123-4567,Your phone number with country code
location,,San Francisco CA USA,Your current location
linkedin_url,,https://linkedin.com/in/john,Your LinkedIn profile URL
website,,https://johnsmith.dev,Your personal website
```

### 3. Text Format (`personal_info_template.txt`)
**Best for**: Simple text editors, quick manual entry
```
NAME: Your Full Name

EMAIL: your.email@example.com

PHONE: +1-555-123-4567

LOCATION: City, State, Country

LINKEDIN: https://linkedin.com/in/username

WEBSITE: https://yourwebsite.com
```

## 🚀 How to Use

### Step 1: Create Template Files
**Option A: Using Profile Manager GUI**
1. Open Profile Manager: `python profile_manager.py`
2. Go to Personal Info tab
3. Click "Create Templates" button
4. Select directory to save templates

**Option B: Using Profile Manager CLI**
1. Run: `python profile_manager.py --cli`
2. Select option 7: "Create Personal Info Templates"
3. Enter directory path (or press Enter for current directory)

**Option C: Manual Download**
Template files are already available in the project directory:
- `personal_info_template.json`
- `personal_info_template.csv`
- `personal_info_template.txt`

### Step 2: Fill Your Information
1. Choose your preferred template format
2. Open the template file in your preferred editor
3. Replace placeholder text with your actual information
4. Save the file with a new name (e.g., `my_personal_info.json`)

### Step 3: Import into Profile Manager
**Option A: Using GUI**
1. Open Profile Manager: `python profile_manager.py`
2. Go to Personal Info tab
3. Click "Load from File" button
4. Select your filled template file
5. Review imported data and save profile

**Option B: Using CLI**
1. Run: `python profile_manager.py --cli`
2. Select option 6: "Import Personal Info from File"
3. Enter path to your filled template file
4. Review and confirm import

## 📋 Field Descriptions

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| **name** | ✅ Yes | Your full name as it appears on resume | "John Michael Smith" |
| **email** | ✅ Yes | Primary email for job applications | "john.smith@email.com" |
| **phone** | ❌ Optional | Phone number with country code | "+1-555-123-4567" |
| **location** | ❌ Optional | Current location for job matching | "San Francisco, CA, USA" |
| **linkedin_url** | ❌ Optional | LinkedIn profile URL | "https://linkedin.com/in/johnsmith" |
| **website** | ❌ Optional | Personal website or portfolio | "https://johnsmith.dev" |

## ✅ Validation Rules

### Email Validation
- Must contain @ symbol and valid domain
- Format: `username@domain.com`
- Example: ✅ `john@email.com` ❌ `john.email.com`

### Phone Validation
- Should include country code for international applications
- Accepts various formats: `+1-555-123-4567`, `(555) 123-4567`, `555.123.4567`
- Minimum 10 digits required

### URL Validation
- Must start with `http://` or `https://`
- Auto-corrected if missing protocol
- Example: `linkedin.com/in/john` → `https://linkedin.com/in/john`

### Location Format
- Be specific for better job matching
- Recommended formats:
  - `City, State, Country` (Full format)
  - `City, State` (US format)
  - `Remote` (For remote workers)

## 🔧 Advanced Features

### Multiple File Format Support
The system automatically detects file format based on:
1. File extension (`.json`, `.csv`, `.txt`)
2. Content analysis (JSON structure, CSV headers, text patterns)
3. Fallback to manual format detection

### Error Handling
- **Validation Errors**: Shows specific issues with your data
- **Format Errors**: Helps identify file format problems
- **Missing Fields**: Warns about required fields
- **Graceful Fallback**: Continues with valid data even if some fields have issues

### Data Security
- Template files contain your personal information
- Keep files secure and don't share publicly
- Consider using Profile Manager's encryption feature for stored profiles
- Delete template files after import if security is a concern

## 🛠️ Troubleshooting

### Common Issues

**"File not found" error**
- Check file path is correct
- Ensure file exists in specified location
- Use absolute path if relative path doesn't work

**"Invalid format" error**
- Verify file format matches expected structure
- Check for syntax errors in JSON files
- Ensure CSV has proper headers
- Verify text format uses correct field labels

**"Validation failed" error**
- Check email format includes @ and domain
- Verify phone number has enough digits
- Ensure URLs start with http:// or https://
- Confirm required fields (name, email) are filled

**"Import partially successful" warning**
- Some fields may have validation issues
- Review warnings and correct problematic fields
- Re-import after fixing issues

### Getting Help
1. Check validation error messages for specific guidance
2. Review template examples for proper format
3. Test with sample files first
4. Use CLI for detailed error information

## 🔄 Integration with Automation

Once imported, your personal information automatically integrates with:
- **LinkedIn Automation**: Auto-fills personal details in job applications
- **Form Field Mapping**: Intelligent matching to various application forms
- **Profile Templates**: Used as base for job-specific profiles
- **Backup System**: Included in profile backups and exports

## 📝 Best Practices

1. **Keep Templates Updated**: Regularly update your template files with current information
2. **Use Descriptive Filenames**: Save filled templates with meaningful names (e.g., `john_smith_2024.json`)
3. **Backup Important Data**: Keep copies of your filled templates
4. **Test Before Use**: Import and validate data before running automation
5. **Security First**: Store personal information securely and delete unnecessary copies

## 🎉 Benefits

- ✅ **Offline Preparation**: Fill information at your own pace
- ✅ **Multiple Formats**: Choose format that works best for you
- ✅ **Validation**: Catch errors before running automation
- ✅ **Reusability**: Save templates for future use
- ✅ **Flexibility**: Easy to update and modify information
- ✅ **Integration**: Seamless connection with existing automation system
