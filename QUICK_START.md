# 🚀 Quick Start Guide - Auto Job Applier

Get the Auto Job Applier running in 5 minutes!

## ⚡ Quick Setup

### 1. Install Ollama (Required)
```bash
# Download from https://ollama.ai
# Then run:
ollama pull llama3:latest
ollama serve
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python auto_job_applier.py
```

## 🎯 First Steps

1. **Load Your Resume**
   - Click "Browse" and select your resume (DOCX, PDF, or TXT)
   - Click "Load Resume"

2. **Search for Jobs**
   - Enter keywords (e.g., "python developer")
   - Set location (e.g., "remote")
   - Click "Search Jobs"

3. **Analyze Jobs**
   - Select a job from the list
   - Click "Analyze Job" for AI-powered analysis

4. **Generate Cover Letters**
   - Select a job and click "Generate Cover Letter"

## 🔧 Build Executable (Optional)

```bash
# Build standalone .exe file
python build_exe.py

# Run the executable
./dist/AutoJobApplier.exe
```

## 🆘 Common Issues

### Ollama Not Working?
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### Resume Won't Load?
- Try DOCX format (most reliable)
- Check file isn't corrupted
- Ensure file permissions

### No Jobs Found?
- Try different keywords
- Check internet connection
- Some job sites may block automated access

## 📞 Need Help?

- Check `AUTO_JOB_APPLIER_README.md` for detailed documentation
- Review `auto_job_applier.log` for error details
- Run `python test_auto_job_applier.py` to test components

---

**Ready to automate your job search! 🎉** 