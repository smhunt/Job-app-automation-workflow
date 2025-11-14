"""
Job posting parser module
Extracts job details, requirements, and qualifications from email content
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class JobPosting:
    """Structured job posting data"""
    company: str = ""
    position: str = ""
    location: str = ""
    job_type: str = ""  # Full-time, Part-time, Contract, etc.
    salary: str = ""
    description: str = ""
    requirements: List[str] = None
    qualifications: List[str] = None
    responsibilities: List[str] = None
    benefits: List[str] = None
    application_url: str = ""
    application_email: str = ""
    raw_content: str = ""

    def __post_init__(self):
        if self.requirements is None:
            self.requirements = []
        if self.qualifications is None:
            self.qualifications = []
        if self.responsibilities is None:
            self.responsibilities = []
        if self.benefits is None:
            self.benefits = []

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class JobParser:
    """Parse job postings from email content"""

    # Common patterns for job posting sections
    SECTION_PATTERNS = {
        'requirements': [
            r'(?:required|requirements?|must have|qualifications?)[:\s]+(.+?)(?=\n\n|\Z)',
            r'(?:what (?:you\'ll need|we\'re looking for))[:\s]+(.+?)(?=\n\n|\Z)',
        ],
        'qualifications': [
            r'(?:qualifications?|preferred|nice to have)[:\s]+(.+?)(?=\n\n|\Z)',
            r'(?:ideal candidate)[:\s]+(.+?)(?=\n\n|\Z)',
        ],
        'responsibilities': [
            r'(?:responsibilities|duties|you will)[:\s]+(.+?)(?=\n\n|\Z)',
            r'(?:what you\'ll do|role description)[:\s]+(.+?)(?=\n\n|\Z)',
        ],
        'benefits': [
            r'(?:benefits|perks|we offer)[:\s]+(.+?)(?=\n\n|\Z)',
        ]
    }

    def __init__(self):
        """Initialize job parser"""
        pass

    def parse(self, email_data: Dict) -> JobPosting:
        """
        Parse job posting from email

        Args:
            email_data: Email data dictionary with subject, body, etc.

        Returns:
            JobPosting object
        """
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        sender = email_data.get('sender', '')

        job = JobPosting(raw_content=body)

        # Extract basic information
        job.company = self._extract_company(subject, body, sender)
        job.position = self._extract_position(subject, body)
        job.location = self._extract_location(body)
        job.job_type = self._extract_job_type(body)
        job.salary = self._extract_salary(body)
        job.description = self._extract_description(body)

        # Extract structured sections
        job.requirements = self._extract_section(body, 'requirements')
        job.qualifications = self._extract_section(body, 'qualifications')
        job.responsibilities = self._extract_section(body, 'responsibilities')
        job.benefits = self._extract_section(body, 'benefits')

        # Extract application details
        job.application_url = self._extract_url(body)
        job.application_email = self._extract_email(body)

        logger.info(f"Parsed job posting: {job.company} - {job.position}")
        return job

    def _extract_company(self, subject: str, body: str, sender: str) -> str:
        """Extract company name"""
        # Try common patterns
        patterns = [
            r'(?:at|@|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+is\s+(?:hiring|looking|seeking)',
            r'Join\s+(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]

        for pattern in patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                return match.group(1).strip()

            match = re.search(pattern, body[:500], re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Try to extract from sender email
        if '@' in sender:
            domain = sender.split('@')[-1].split('.')[0]
            return domain.title()

        return "Unknown Company"

    def _extract_position(self, subject: str, body: str) -> str:
        """Extract position/job title"""
        # Common job title patterns
        patterns = [
            r'(?:position|role|job|opening)[:\s]+(.+?)(?:\||at|@|\n)',
            r'hiring\s+(?:a|an)?\s*(.+?)(?:\||at|@|\n)',
            r'(?:apply for|looking for)\s+(?:a|an)?\s*(.+?)(?:\||at|@|\n)',
        ]

        # Try subject first
        for pattern in patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Clean up common suffixes
                title = re.sub(r'\s*\([^)]*\)', '', title)
                return title

        # Try body
        for pattern in patterns:
            match = re.search(pattern, body[:300], re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                title = re.sub(r'\s*\([^)]*\)', '', title)
                return title

        return "Unknown Position"

    def _extract_location(self, body: str) -> str:
        """Extract job location"""
        patterns = [
            r'(?:location|based in|office)[:\s]+(.+?)(?:\n|,|\.)',
            r'(?:remote|hybrid|on-site|in-office)',
            r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, STATE
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*(?:[A-Z][a-z]+|Canada|USA))',  # City, Country
        ]

        for pattern in patterns:
            match = re.search(pattern, body[:1000], re.IGNORECASE)
            if match:
                return match.group(0).strip() if pattern.startswith('(?:remote') else match.group(1).strip()

        return "Location not specified"

    def _extract_job_type(self, body: str) -> str:
        """Extract job type (full-time, part-time, etc.)"""
        patterns = {
            'Full-time': r'\bfull[- ]?time\b',
            'Part-time': r'\bpart[- ]?time\b',
            'Contract': r'\bcontract\b',
            'Temporary': r'\btemporary\b',
            'Internship': r'\binternship\b',
            'Freelance': r'\bfreelance\b',
        }

        for job_type, pattern in patterns.items():
            if re.search(pattern, body, re.IGNORECASE):
                return job_type

        return "Not specified"

    def _extract_salary(self, body: str) -> str:
        """Extract salary information"""
        patterns = [
            r'\$[\d,]+(?:\s*-\s*\$?[\d,]+)?\s*(?:per year|/year|annually|/yr)?',
            r'(?:salary|compensation)[:\s]+\$?[\d,]+(?:\s*-\s*\$?[\d,]+)?',
            r'[\d,]+k\s*-\s*[\d,]+k',
        ]

        for pattern in patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                return match.group(0).strip()

        return "Not specified"

    def _extract_description(self, body: str) -> str:
        """Extract job description"""
        # Get first few paragraphs as description
        paragraphs = [p.strip() for p in body.split('\n\n') if p.strip()]
        description_parts = []

        for p in paragraphs[:5]:  # First 5 paragraphs
            # Skip if looks like a section header
            if re.match(r'^[A-Z][a-z]+\s*:?\s*$', p):
                continue
            description_parts.append(p)

        return '\n\n'.join(description_parts[:3])  # First 3 relevant paragraphs

    def _extract_section(self, body: str, section_name: str) -> List[str]:
        """Extract items from a specific section"""
        items = []

        if section_name not in self.SECTION_PATTERNS:
            return items

        for pattern in self.SECTION_PATTERNS[section_name]:
            match = re.search(pattern, body, re.IGNORECASE | re.DOTALL)
            if match:
                section_text = match.group(1)
                # Extract bullet points or numbered items
                items = self._extract_list_items(section_text)
                if items:
                    break

        return items

    def _extract_list_items(self, text: str) -> List[str]:
        """Extract list items from text"""
        items = []

        # Try bullet points
        bullet_pattern = r'[•\-\*]\s*(.+?)(?=\n[•\-\*]|\n\n|\Z)'
        matches = re.findall(bullet_pattern, text, re.DOTALL)
        if matches:
            items = [m.strip() for m in matches]

        # Try numbered list
        if not items:
            number_pattern = r'\d+[\.)]\s*(.+?)(?=\n\d+[\.)]|\n\n|\Z)'
            matches = re.findall(number_pattern, text, re.DOTALL)
            if matches:
                items = [m.strip() for m in matches]

        # Try newline-separated items
        if not items:
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            items = [line for line in lines if len(line) > 10]  # Filter out short lines

        return items

    def _extract_url(self, body: str) -> str:
        """Extract application URL"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+(?:apply|job|career|position)[^\s<>"{}|\\^`\[\]]*'
        match = re.search(url_pattern, body, re.IGNORECASE)

        if match:
            return match.group(0)

        # Try generic URL
        generic_url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        matches = re.findall(generic_url_pattern, body)
        if matches:
            return matches[0]  # Return first URL

        return ""

    def _extract_email(self, body: str) -> str:
        """Extract application email"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, body)

        # Filter out common non-application emails
        exclude_patterns = ['noreply', 'no-reply', 'unsubscribe']

        for email in matches:
            if not any(pattern in email.lower() for pattern in exclude_patterns):
                return email

        return ""

    def is_job_posting(self, email_data: Dict) -> bool:
        """
        Determine if email is a job posting

        Args:
            email_data: Email data dictionary

        Returns:
            True if likely a job posting
        """
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()

        job_keywords = [
            'job', 'position', 'opening', 'opportunity', 'hiring',
            'career', 'employment', 'vacancy', 'role', 'apply'
        ]

        # Check subject
        if any(keyword in subject for keyword in job_keywords):
            return True

        # Check first 500 chars of body
        body_start = body[:500]
        keyword_count = sum(1 for keyword in job_keywords if keyword in body_start)

        return keyword_count >= 2
