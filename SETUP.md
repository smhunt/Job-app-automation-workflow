# Setup Guide

Complete step-by-step guide to set up your Job Application Automation System.

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or if you prefer using a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Set Up Gmail API

### 2.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it (e.g., "Job Application Automation")
4. Click "Create"

### 2.2 Enable Gmail API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click "Enable"

### 2.3 Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External
   - App name: Job Application Automation
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add Gmail API read scope
   - Test users: Add your email (sean.jobs@ecoworks.ca)
4. Back to credentials:
   - Application type: Desktop app
   - Name: Job Automation Client
5. Click "Create"
6. Download the credentials JSON file
7. Save it as `credentials.json` in the project root directory

### 2.4 First-Time Authentication

When you first run the application, it will:
1. Open your browser for authentication
2. Ask you to sign in to your Google account
3. Request permission to read your Gmail
4. Save a token for future use

## Step 3: Get Anthropic API Key

1. Sign up at [Anthropic Console](https://console.anthropic.com/)
2. Navigate to API Keys section
3. Create a new API key
4. Copy the key (you'll need it for configuration)

## Step 4: Configure the Application

1. Create your configuration file:
   ```bash
   cp config.example.yml config.yml
   ```

2. Edit `config.yml`:
   ```yaml
   email:
     address: "sean.jobs@ecoworks.ca"
     labels: ["INBOX"]  # Or ["Jobs"] if you use a specific label
     check_interval: 300  # Check every 5 minutes

   api:
     anthropic_key: "sk-ant-..."  # Paste your Anthropic API key here

   templates:
     resume: "templates/resume.txt"
     cover_letter: "templates/cover_letter_template.txt"

   output:
     directory: "output"
     format: "pdf"

   logging:
     level: "INFO"
     file: "logs/job_automation.log"
   ```

## Step 5: Add Your Resume and Cover Letter

1. Edit `templates/resume.txt`:
   - Replace all bracketed placeholders with your actual information
   - Include your real work experience, education, skills
   - Be honest and accurate (the AI will customize, not fabricate)

2. Edit `templates/cover_letter_template.txt`:
   - Update with your writing style
   - The AI will use this as a template for customization

## Step 6: Test the Setup

### Test Gmail Connection

```bash
python main.py --create-config  # Creates example config if needed
```

### Test with a Sample Job Email

1. Forward a job posting to sean.jobs@ecoworks.ca
2. Run the automation:
   ```bash
   python main.py --monitor
   ```

Or process a specific email by ID (get ID from Gmail):
```bash
python main.py --email-id <message-id>
```

## Step 7: Run in Monitor Mode

Start continuous monitoring:

```bash
python main.py --monitor
```

The system will:
- Check for new emails every 5 minutes (configurable)
- Detect job postings automatically
- Generate customized application packages
- Save everything to the `output/` directory

## Folder Structure After Setup

```
Job-app-automation-workflow/
├── credentials.json         # Gmail API credentials (gitignored)
├── config.yml              # Your configuration (gitignored)
├── token.pickle            # Saved Gmail auth (gitignored)
├── templates/
│   ├── resume.txt          # Your resume (gitignored)
│   └── cover_letter_template.txt  # Your template (gitignored)
├── output/                 # Generated applications (gitignored)
│   ├── Company_Position_analysis.md
│   ├── Company_Position_resume.txt
│   ├── Company_Position_cover_letter.txt
│   └── Company_Position_APPLICATION_GUIDE.md
└── logs/                   # Log files (gitignored)
    └── job_automation.log
```

## Troubleshooting

### Gmail Authentication Issues

**Error: "Access blocked: This app's request is invalid"**
- Solution: Make sure you've configured the OAuth consent screen and added your email as a test user

**Error: "credentials.json not found"**
- Solution: Download OAuth credentials from Google Cloud Console and save as `credentials.json`

### API Issues

**Error: "Anthropic API key not provided"**
- Solution: Add your API key to `config.yml` under `api.anthropic_key`

**Error: "Rate limit exceeded"**
- Solution: Wait a few minutes or upgrade your Anthropic API plan

### Template Issues

**Error: "Template file not found"**
- Solution: Create `templates/resume.txt` and `templates/cover_letter_template.txt` with your information

## Tips for Best Results

1. **Keep your resume updated**: Update `templates/resume.txt` regularly
2. **Use specific labels**: Create a "Jobs" label in Gmail and configure the app to monitor it
3. **Review outputs**: Always review and personalize the generated materials
4. **Test with various job types**: Different industries may require adjustments
5. **Monitor logs**: Check `logs/job_automation.log` for issues

## Running in the Background

### Linux/Mac (using screen or tmux)

```bash
screen -S job-automation
python main.py --monitor
# Press Ctrl+A then D to detach
# Reattach with: screen -r job-automation
```

### Using systemd (Linux)

Create `/etc/systemd/system/job-automation.service`:

```ini
[Unit]
Description=Job Application Automation
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/Job-app-automation-workflow
ExecStart=/path/to/venv/bin/python main.py --monitor
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable job-automation
sudo systemctl start job-automation
```

## Security Notes

- Never commit `credentials.json`, `token.pickle`, or `config.yml` to git
- Keep your API keys secure
- The `.gitignore` file is configured to protect sensitive data
- Review all generated applications before submitting

## Next Steps

Once set up:
1. Forward job postings to sean.jobs@ecoworks.ca
2. Check the `output/` directory for generated packages
3. Review and personalize the materials
4. Apply with confidence!

Good luck with your job search!
