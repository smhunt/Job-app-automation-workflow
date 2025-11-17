# Job Application Automation System - Architecture Specification

## System Overview

An intelligent automation system that monitors Gmail for job postings, uses AI to customize application materials, identifies skill gaps, and generates ready-to-submit application packages.

## Core Requirements

### Functional Requirements

1. **Email Monitoring**
   - Connect to Gmail via OAuth2
   - Monitor specific labels/folders
   - Detect job posting emails automatically
   - Support both polling and real-time monitoring

2. **Job Posting Analysis**
   - Extract company, position, location, salary
   - Parse requirements and qualifications
   - Identify responsibilities and benefits
   - Extract application URLs and contact emails

3. **AI-Powered Customization**
   - Analyze candidate fit (0-100 score)
   - Customize resume for specific role
   - Generate tailored cover letter
   - Identify gaps and suggest strategies
   - Support multiple AI providers (Anthropic, OpenAI)

4. **Cost Optimization**
   - Support batch processing for 50% savings
   - Provider switching (Claude vs GPT-4)
   - Model selection (quality vs cost)
   - Cost tracking and reporting

5. **Package Generation**
   - Create customized resume (TXT, PDF)
   - Generate cover letter (TXT, PDF)
   - Produce analysis report (Markdown)
   - Create application guide with instructions
   - Save job details for reference

### Non-Functional Requirements

1. **Security**
   - OAuth2 authentication for Gmail
   - API keys stored securely in config
   - Sensitive files gitignored
   - No credentials in code

2. **Reliability**
   - Graceful error handling
   - Comprehensive logging
   - Token refresh handling
   - Network retry logic

3. **Usability**
   - Simple YAML configuration
   - CLI interface
   - Clear documentation
   - Helpful error messages

4. **Cost Efficiency**
   - Batch API support (50% savings)
   - Model selection options
   - Cost estimation tools
   - Usage tracking

## System Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Main Orchestrator                        │
│                      (main.py)                               │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌────────────────┐    ┌──────────────┐
│ Email Monitor │    │  Job Parser    │    │ AI Provider  │
│ (Gmail API)   │    │  (Extraction)  │    │ (Multi)      │
└───────────────┘    └────────────────┘    └──────────────┘
                                                    │
                                    ┌───────────────┼──────────────┐
                                    ▼               ▼              ▼
                            ┌──────────────┐ ┌──────────┐ ┌──────────┐
                            │   Anthropic  │ │  OpenAI  │ │  OpenAI  │
                            │   (Claude)   │ │(Real-time)│ │ (Batch)  │
                            └──────────────┘ └──────────┘ └──────────┘
                                    │               │              │
                                    └───────────────┼──────────────┘
                                                    ▼
                                           ┌─────────────────┐
                                           │  Gap Analyzer   │
                                           │  (Reports)      │
                                           └─────────────────┘
                                                    │
                                                    ▼
                                           ┌─────────────────┐
                                           │ Package Gen     │
                                           │ (PDF/TXT/MD)    │
                                           └─────────────────┘
                                                    │
                                                    ▼
                                           ┌─────────────────┐
                                           │  Output Files   │
                                           │  (Application)  │
                                           └─────────────────┘
```

### Module Specifications

#### 1. Email Monitor (src/email_monitor.py)

**Purpose:** Interface with Gmail API to monitor and retrieve emails

**Key Classes:**
- `EmailMonitor`: Main monitoring class

**Key Methods:**
```python
def __init__(credentials_path, token_path)
def _authenticate() -> service
def get_unread_emails(labels, max_results) -> List[Dict]
def get_email_by_id(message_id) -> Dict
def search_emails(query, max_results) -> List[Dict]
def mark_as_read(message_id)
def _get_email_data(message_id) -> Dict
def _get_email_body(payload) -> str
```

**Data Structures:**
```python
Email = {
    'id': str,
    'subject': str,
    'sender': str,
    'date': str,
    'body': str,
    'snippet': str
}
```

#### 2. Job Parser (src/job_parser.py)

**Purpose:** Extract structured data from job posting emails

**Key Classes:**
- `JobPosting`: Dataclass for job data
- `JobParser`: Parser class

**Key Methods:**
```python
def parse(email_data) -> JobPosting
def is_job_posting(email_data) -> bool
def _extract_company(subject, body, sender) -> str
def _extract_position(subject, body) -> str
def _extract_location(body) -> str
def _extract_requirements(body) -> List[str]
def _extract_url(body) -> str
def _extract_email(body) -> str
```

**Data Structures:**
```python
JobPosting = {
    'company': str,
    'position': str,
    'location': str,
    'job_type': str,
    'salary': str,
    'description': str,
    'requirements': List[str],
    'qualifications': List[str],
    'responsibilities': List[str],
    'benefits': List[str],
    'application_url': str,
    'application_email': str,
    'raw_content': str
}
```

#### 3. AI Customizers

**3a. Anthropic Customizer (src/ai_customizer.py)**

**Purpose:** Claude API integration for AI customization

**Key Methods:**
```python
def __init__(api_key)
def customize_resume(base_resume, job_posting) -> str
def customize_cover_letter(template, job_posting, resume) -> str
def analyze_fit(resume, job_posting) -> Dict
def _build_resume_prompt(resume, job_posting) -> str
def _build_cover_letter_prompt(template, job_posting, resume) -> str
def _build_analysis_prompt(resume, job_posting) -> str
def _parse_analysis(analysis_text) -> Dict
```

**3b. OpenAI Customizer (src/openai_customizer.py)**

**Purpose:** OpenAI API integration with batch support

**Key Methods:**
```python
def __init__(api_key, use_batch)
def customize_resume(base_resume, job_posting) -> str
def customize_cover_letter(template, job_posting, resume) -> str
def analyze_fit(resume, job_posting) -> Dict
def _process_batch(tasks) -> List[str]
def _log_cost(usage)
def estimate_job_cost() -> Dict
```

**Analysis Structure:**
```python
Analysis = {
    'match_score': int,  # 0-100
    'strengths': List[str],
    'gaps': List[str],
    'strategies': List[str],
    'tips': List[str],
    'full_analysis': str
}
```

#### 4. Gap Analyzer (src/gap_analyzer.py)

**Purpose:** Generate analysis reports and summaries

**Key Methods:**
```python
def generate_report(job_posting, analysis, resume, cover_letter) -> str
def create_quick_summary(analysis, job_posting) -> str
def _format_list(items) -> str
```

#### 5. Package Generator (src/package_generator.py)

**Purpose:** Create output files in various formats

**Key Methods:**
```python
def __init__(output_dir)
def generate_package(job_posting, resume, cover_letter, report) -> Dict[str, str]
def create_application_summary(files, job_posting, quick_summary) -> str
def _sanitize_filename(name) -> str
def _generate_pdfs(base_name, resume, cover_letter) -> Dict[str, str]
```

**Output Structure:**
```
output/
└── Company_Position_20240115_143022/
    ├── Company_Position_resume.txt
    ├── Company_Position_resume.pdf
    ├── Company_Position_cover_letter.txt
    ├── Company_Position_cover_letter.pdf
    ├── Company_Position_analysis.md
    ├── Company_Position_APPLICATION_GUIDE.md
    └── Company_Position_job_details.json
```

#### 6. Cost Tracker (src/cost_tracker.py)

**Purpose:** Track and compare API costs

**Key Methods:**
```python
@classmethod
def estimate_cost(provider, model, use_batch) -> Dict
@classmethod
def compare_all_options() -> str
@classmethod
def recommend_config(budget, applications) -> Dict
```

#### 7. Utilities (src/utils.py)

**Purpose:** Common utility functions

**Key Methods:**
```python
def setup_logging(log_level, log_file)
def load_config(config_path) -> Dict
def load_template(template_path) -> str
def validate_config(config) -> bool
def create_default_config(output_path)
def ensure_directories(config)
```

### Configuration Schema

```yaml
email:
  address: string           # Gmail address to monitor
  labels: [string]          # Labels to filter (e.g., ['INBOX', 'Jobs'])
  check_interval: int       # Seconds between checks (default: 300)

api:
  provider: string          # 'anthropic' or 'openai'

  # Anthropic settings
  anthropic_key: string     # Claude API key

  # OpenAI settings
  openai_key: string        # OpenAI API key
  openai_model: string      # 'gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo'
  use_batch: boolean        # true = 50% savings, 24hr processing

templates:
  resume: string            # Path to base resume
  cover_letter: string      # Path to cover letter template

output:
  directory: string         # Output directory path
  format: string            # 'pdf' or 'txt'

logging:
  level: string             # 'DEBUG', 'INFO', 'WARNING', 'ERROR'
  file: string              # Log file path
```

## Workflow

### Main Workflow

1. **Initialization**
   ```
   Load config → Validate → Setup logging → Initialize components
   ```

2. **Monitoring Mode**
   ```
   Loop:
     Check for new emails
     For each email:
       ├─ Is job posting? → Skip if not
       ├─ Parse job details
       ├─ Analyze fit
       ├─ Customize resume
       ├─ Generate cover letter
       ├─ Create analysis report
       ├─ Generate package
       └─ Mark as read
     Sleep(check_interval)
   ```

3. **Single Email Mode**
   ```
   Get email by ID → Process (same as above) → Done
   ```

### Processing Workflow

```
Email → Job Parser → Validation
                        ↓
                   AI Provider
                        ↓
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
    Analysis        Resume          Cover Letter
        └───────────────┼───────────────┘
                        ▼
                  Gap Analyzer
                        ↓
                Package Generator
                        ↓
        ┌───────────────┼───────────────┬───────────┐
        ▼               ▼               ▼           ▼
    Resume.pdf   Cover_Letter.pdf  Analysis.md  Guide.md
```

### Batch Processing Workflow (OpenAI)

```
Jobs Queue → Create JSONL → Upload to OpenAI
                                    ↓
                            Submit Batch Job
                                    ↓
                            Poll Status (30s)
                                    ↓
                         Wait up to 24 hours
                                    ↓
                           Download Results
                                    ↓
                            Parse & Generate
```

## API Integration Details

### Gmail API

**Authentication:** OAuth2 with local server flow
**Scopes:** `https://www.googleapis.com/auth/gmail.readonly`
**Rate Limits:** 1 billion quota units/day (generous)

**Key Endpoints:**
- `users.messages.list()` - List messages
- `users.messages.get()` - Get message details
- `users.messages.modify()` - Mark as read

### Anthropic API (Claude)

**Authentication:** API key in header
**Model:** claude-3-5-sonnet-20241022
**Rate Limits:** Varies by plan

**Pricing (per 1M tokens):**
- Input: $3.00
- Output: $15.00
- **Estimated cost per job: $0.60**

### OpenAI API (GPT-4)

**Authentication:** API key in header
**Models:** gpt-4o, gpt-4o-mini, gpt-4-turbo
**Rate Limits:** Varies by plan

**Pricing (per 1M tokens) - Real-time:**
- GPT-4o: Input $2.50, Output $10.00 → **$0.42/job**
- GPT-4o-mini: Input $0.15, Output $0.60 → **$0.08/job**

**Pricing (per 1M tokens) - Batch (50% off):**
- GPT-4o: Input $1.25, Output $5.00 → **$0.21/job**
- GPT-4o-mini: Input $0.075, Output $0.30 → **$0.04/job** ⭐

## Error Handling

### Gmail Errors
- **Invalid credentials:** Regenerate token.pickle
- **Network errors:** Retry with exponential backoff
- **Quota exceeded:** Wait and retry

### AI Provider Errors
- **Invalid API key:** Clear error message
- **Rate limit:** Wait and retry with backoff
- **Timeout:** Retry with longer timeout
- **Context too long:** Truncate intelligently

### File System Errors
- **Missing templates:** Clear error message
- **Permission denied:** Check directory permissions
- **Disk full:** Clear error with space required

## Security Considerations

1. **Credentials**
   - OAuth tokens in `token.pickle` (gitignored)
   - API keys in `config.yml` (gitignored)
   - Never commit credentials

2. **Data Privacy**
   - All processing local
   - Email data not stored permanently
   - Output files contain personal info (gitignored)

3. **Input Validation**
   - Validate configuration before use
   - Sanitize filenames
   - Validate email data structure

## Testing Strategy

### Unit Tests
- Email parser accuracy
- Job posting detection
- Data extraction
- Configuration validation

### Integration Tests
- Gmail API connection
- AI provider responses
- File generation
- End-to-end workflow

### Manual Tests
- Real job posting emails
- Various email formats
- Different AI providers
- Batch vs real-time

## Performance Considerations

1. **Email Polling**
   - Configurable interval (default: 5 min)
   - Efficient label filtering
   - Process only unread

2. **AI Processing**
   - Batch API for cost savings
   - Concurrent processing possible
   - Token usage optimization

3. **File Generation**
   - Lazy PDF generation (optional)
   - Efficient template loading
   - Minimal disk I/O

## Deployment

### Development
```bash
python main.py --monitor
```

### Production (systemd)
```ini
[Unit]
Description=Job Application Automation

[Service]
Type=simple
ExecStart=/path/to/venv/bin/python main.py --monitor
Restart=always

[Install]
WantedBy=multi-user.target
```

### Production (screen/tmux)
```bash
screen -S job-automation
python main.py --monitor
# Ctrl+A, D to detach
```

## Monitoring & Logging

**Log Levels:**
- DEBUG: Detailed processing info
- INFO: Key events (email received, package generated)
- WARNING: Recoverable issues
- ERROR: Failures requiring attention

**Key Metrics:**
- Emails processed
- Jobs detected
- API costs
- Processing time
- Error rate

## Future Enhancements

### Phase 2
- [ ] Web dashboard for monitoring
- [ ] Application tracking database
- [ ] Email templates for follow-ups
- [ ] Interview preparation materials
- [ ] Skills gap learning recommendations

### Phase 3
- [ ] LinkedIn integration
- [ ] Indeed/Glassdoor scraping
- [ ] Company research automation
- [ ] Salary negotiation insights
- [ ] Application status tracking

### Phase 4
- [ ] Multi-user support
- [ ] Team collaboration features
- [ ] Analytics dashboard
- [ ] A/B testing for applications
- [ ] Success rate tracking

## Documentation Structure

```
├── README.md              # Quick overview and setup
├── SETUP.md              # Detailed setup guide
├── QUICKSTART.md         # 5-minute setup
├── PRICING.md            # Cost comparison and optimization
├── CLAUDE.md             # This architecture document
├── API.md                # API reference (future)
└── CONTRIBUTING.md       # Contribution guidelines (future)
```

## Success Metrics

1. **Time Savings**
   - Target: 2-3 hours saved per application
   - Manual: ~3 hours per application
   - Automated: ~5 minutes review time

2. **Cost Efficiency**
   - Target: <$0.10 per application
   - Achieved: $0.04-0.60 depending on provider

3. **Quality**
   - Target: >80% match score on average
   - Customized materials indistinguishable from manual

4. **User Satisfaction**
   - Easy setup (<30 min)
   - Clear documentation
   - Reliable operation

## Conclusion

This system provides a comprehensive, cost-effective solution for automating job applications while maintaining quality and personalization. The modular architecture allows for easy extension and maintenance, while the multi-provider support ensures flexibility in cost vs. quality trade-offs.

---

**Version:** 1.0.0
**Last Updated:** 2024-01-15
**Status:** Production Ready ✅
