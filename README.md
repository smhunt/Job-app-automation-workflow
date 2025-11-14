# Job Application Automation Workflow

Automated job application system that monitors your email (sean.jobs@ecoworks.ca), analyzes job postings, customizes your resume and cover letter, identifies gaps, and helps you apply efficiently.

## Features

- 📧 **Email Monitoring**: Automatically monitors Gmail inbox for job postings
- 🤖 **AI-Powered Customization**: Uses Claude API to tailor your resume and cover letter
- 🔍 **Gap Analysis**: Identifies skill/experience gaps and suggests strategies
- 📝 **Application Package**: Generates customized application materials
- ⚡ **Easy Application**: Provides streamlined application instructions

## Quick Start

### Prerequisites

- Python 3.8+
- Gmail account (sean.jobs@ecoworks.ca)
- Anthropic API key (for Claude AI)

### Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your settings:
   ```bash
   cp config.example.yml config.yml
   # Edit config.yml with your details
   ```

4. Set up Gmail API:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download credentials and save as `credentials.json`

5. Add your resume and cover letter template:
   - Place your resume in `templates/resume.txt` or `templates/resume.pdf`
   - Place your cover letter template in `templates/cover_letter_template.txt`

### Usage

#### Manual Mode (Process Specific Email)
```bash
python main.py --email-id <email-id>
```

#### Auto Mode (Monitor Inbox)
```bash
python main.py --monitor
```

#### Forward Job Email
Simply forward any job posting email to sean.jobs@ecoworks.ca and the system will:
1. Extract job details
2. Analyze requirements
3. Customize your application
4. Generate a report with gaps and strategies
5. Create ready-to-submit materials

## Project Structure

```
├── main.py                      # Main automation script
├── src/
│   ├── email_monitor.py         # Gmail API integration
│   ├── job_parser.py            # Job posting parser
│   ├── ai_customizer.py         # AI-powered customization
│   ├── gap_analyzer.py          # Gap analysis module
│   ├── package_generator.py     # Application package generator
│   └── utils.py                 # Utility functions
├── templates/
│   ├── resume.txt               # Your base resume
│   └── cover_letter_template.txt # Your cover letter template
├── output/                      # Generated applications
├── config.yml                   # Configuration file
├── credentials.json             # Gmail API credentials
└── requirements.txt             # Python dependencies
```

## Configuration

Edit `config.yml`:

```yaml
email:
  address: "sean.jobs@ecoworks.ca"
  labels: ["Jobs", "INBOX"]  # Gmail labels to monitor

api:
  anthropic_key: "your-api-key-here"

templates:
  resume: "templates/resume.txt"
  cover_letter: "templates/cover_letter_template.txt"

output:
  directory: "output"
  format: "pdf"  # pdf or docx
```

## Output

For each job, the system generates:

1. **Customized Resume** (`output/<company>_<position>_resume.pdf`)
2. **Customized Cover Letter** (`output/<company>_<position>_cover_letter.pdf`)
3. **Analysis Report** (`output/<company>_<position>_analysis.md`):
   - Job requirements breakdown
   - Your qualifications match
   - Identified gaps
   - Strategies to address gaps
   - Application tips
4. **Application Instructions** (Quick apply links and steps)

## Example Workflow

1. You receive a job posting email at sean.jobs@ecoworks.ca
2. System detects the email automatically (if in monitor mode)
3. Extracts job details (company, position, requirements, etc.)
4. Analyzes your fit for the role
5. Customizes resume to highlight relevant experience
6. Generates tailored cover letter
7. Creates gap analysis report
8. Provides easy application instructions

## Troubleshooting

- **Gmail Authentication Issues**: Ensure OAuth consent screen is configured and credentials.json is valid
- **API Errors**: Check your Anthropic API key in config.yml
- **Missing Templates**: Ensure resume and cover letter templates exist

## License

MIT License