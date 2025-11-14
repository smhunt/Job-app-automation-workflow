# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Gmail account (sean.jobs@ecoworks.ca)
- [ ] Anthropic API key ([Get one here](https://console.anthropic.com/))

## Fast Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy config template
cp config.example.yml config.yml

# 3. Edit config.yml - add your Anthropic API key
nano config.yml  # or your preferred editor

# 4. Set up Gmail API
# Follow SETUP.md Section 2 for detailed Gmail API setup
# Download credentials.json from Google Cloud Console

# 5. Add your resume and cover letter
nano templates/resume.txt
nano templates/cover_letter_template.txt

# 6. Run!
python main.py --monitor
```

## Most Common Commands

```bash
# Monitor inbox continuously
python main.py --monitor

# Process a specific email
python main.py --email-id <message-id>

# Create example config
python main.py --create-config

# Monitor with custom interval (in seconds)
python main.py --monitor --interval 600
```

## What Happens When You Run It?

1. **Monitors** your Gmail inbox (sean.jobs@ecoworks.ca)
2. **Detects** job posting emails automatically
3. **Extracts** job requirements and details
4. **Analyzes** your fit for the role
5. **Customizes** your resume for this specific job
6. **Generates** a tailored cover letter
7. **Creates** a gap analysis report with strategies
8. **Saves** everything to `output/` directory

## Example Output

For each job, you get:

```
output/
└── Acme_Corp_Software_Engineer_20240115_143022/
    ├── Acme_Corp_Software_Engineer_resume.txt
    ├── Acme_Corp_Software_Engineer_cover_letter.txt
    ├── Acme_Corp_Software_Engineer_analysis.md
    ├── Acme_Corp_Software_Engineer_APPLICATION_GUIDE.md
    └── Acme_Corp_Software_Engineer_job_details.json
```

## Typical Workflow

1. **Receive** job posting email at sean.jobs@ecoworks.ca
2. **Wait** for automation to process it (or run manually)
3. **Check** `output/` directory for your custom package
4. **Review** the APPLICATION_GUIDE.md
5. **Read** the analysis.md for gaps and strategies
6. **Customize** if needed (but AI does most of the work!)
7. **Apply** using the materials

## Sample Analysis Output

The system tells you:

- **Match Score**: 85/100 ⭐
- **Your Strengths**: What makes you a great fit
- **Gaps**: What you might be missing
- **Strategies**: How to address gaps and stand out
- **Tips**: Specific advice for this application

## Troubleshooting Fast Fixes

### Can't authenticate with Gmail?
```bash
# Delete old token and try again
rm token.pickle
python main.py --monitor
```

### API errors?
```bash
# Check your API key in config.yml
cat config.yml | grep anthropic_key
```

### No templates found?
```bash
# Make sure templates exist
ls templates/
# Should show: resume.txt  cover_letter_template.txt
```

### Want to test without monitoring?
```bash
# Just check for unread emails once
python -c "from src.email_monitor import EmailMonitor; em = EmailMonitor(); print(len(em.get_unread_emails()), 'unread emails')"
```

## Pro Tips

1. **Create a Gmail filter**: Auto-label job emails with "Jobs"
2. **Update config** to monitor only that label:
   ```yaml
   email:
     labels: ["Jobs"]
   ```
3. **Run in background**: Use `screen` or `tmux`
4. **Check logs**: `tail -f logs/job_automation.log`
5. **Keep resume current**: Update `templates/resume.txt` regularly

## Cost Estimate

- **Gmail API**: Free
- **Anthropic API**:
  - ~$0.50-1.00 per job application
  - Claude Sonnet pricing: ~$3 per million tokens
  - Each job uses ~200-400K tokens (analysis + customization)

## Need More Help?

- Full setup guide: See `SETUP.md`
- Understanding the code: See `README.md`
- Issues: Check logs in `logs/job_automation.log`

## Ready to Apply?

Forward any job posting to sean.jobs@ecoworks.ca and let the automation do the heavy lifting!

Good luck! 🚀
