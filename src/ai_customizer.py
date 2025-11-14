"""
AI-powered customization module
Uses Claude API to customize resumes and cover letters
"""

import os
from typing import Dict, Optional
import anthropic
import logging

logger = logging.getLogger(__name__)


class AICustomizer:
    """AI-powered resume and cover letter customizer"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI customizer

        Args:
            api_key: Anthropic API key (or use ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def customize_resume(self, base_resume: str, job_posting: Dict) -> str:
        """
        Customize resume for specific job

        Args:
            base_resume: Original resume text
            job_posting: Parsed job posting data

        Returns:
            Customized resume text
        """
        prompt = self._build_resume_prompt(base_resume, job_posting)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            customized_resume = message.content[0].text
            logger.info(f"Successfully customized resume for {job_posting.get('position', 'position')}")
            return customized_resume

        except Exception as e:
            logger.error(f"Error customizing resume: {e}")
            return base_resume

    def customize_cover_letter(self, template: str, job_posting: Dict, resume: str) -> str:
        """
        Generate customized cover letter

        Args:
            template: Cover letter template
            job_posting: Parsed job posting data
            resume: Applicant's resume

        Returns:
            Customized cover letter
        """
        prompt = self._build_cover_letter_prompt(template, job_posting, resume)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            cover_letter = message.content[0].text
            logger.info(f"Successfully generated cover letter for {job_posting.get('position', 'position')}")
            return cover_letter

        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return template

    def _build_resume_prompt(self, resume: str, job_posting: Dict) -> str:
        """Build prompt for resume customization"""
        company = job_posting.get('company', 'the company')
        position = job_posting.get('position', 'this position')
        requirements = job_posting.get('requirements', [])
        responsibilities = job_posting.get('responsibilities', [])

        requirements_text = '\n'.join(f"- {req}" for req in requirements) if requirements else "Not specified"
        responsibilities_text = '\n'.join(f"- {resp}" for resp in responsibilities) if responsibilities else "Not specified"

        prompt = f"""You are an expert resume writer helping customize a resume for a specific job application.

JOB DETAILS:
Company: {company}
Position: {position}

Key Requirements:
{requirements_text}

Key Responsibilities:
{responsibilities_text}

ORIGINAL RESUME:
{resume}

TASK:
Customize this resume to highlight relevant experience and skills for this specific job. Follow these guidelines:

1. Keep all factual information accurate - do not fabricate experience
2. Reorder and emphasize experiences most relevant to this role
3. Use keywords from the job posting naturally
4. Quantify achievements where possible
5. Tailor the summary/objective to this specific position
6. Highlight transferable skills that match requirements
7. Maintain professional formatting and clarity
8. Keep the same overall structure but optimize content

Return ONLY the customized resume text, no additional commentary."""

        return prompt

    def _build_cover_letter_prompt(self, template: str, job_posting: Dict, resume: str) -> str:
        """Build prompt for cover letter generation"""
        company = job_posting.get('company', 'the company')
        position = job_posting.get('position', 'this position')
        description = job_posting.get('description', '')
        requirements = job_posting.get('requirements', [])

        requirements_text = '\n'.join(f"- {req}" for req in requirements) if requirements else "Not specified"

        prompt = f"""You are an expert cover letter writer helping create a compelling cover letter for a job application.

JOB DETAILS:
Company: {company}
Position: {position}

Job Description:
{description[:500]}...

Key Requirements:
{requirements_text}

APPLICANT'S RESUME:
{resume[:1500]}...

COVER LETTER TEMPLATE (use as style guide):
{template}

TASK:
Write a compelling, personalized cover letter for this application. Follow these guidelines:

1. Address the hiring manager professionally (use "Dear Hiring Manager" if name unknown)
2. Show genuine enthusiasm for the company and role
3. Highlight 2-3 key experiences from resume that match job requirements
4. Explain why you're interested in this specific company and role
5. Demonstrate understanding of the company's mission/values (if mentioned in job posting)
6. Be confident but not arrogant
7. Keep it concise (3-4 paragraphs, under 400 words)
8. End with a strong call to action
9. Match the tone of the template provided

Return ONLY the cover letter text, no additional commentary."""

        return prompt

    def analyze_fit(self, resume: str, job_posting: Dict) -> Dict:
        """
        Analyze candidate's fit for the position

        Args:
            resume: Applicant's resume
            job_posting: Parsed job posting

        Returns:
            Dictionary with analysis results
        """
        prompt = self._build_analysis_prompt(resume, job_posting)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            analysis_text = message.content[0].text
            logger.info("Successfully analyzed job fit")

            # Parse the analysis into structured format
            return self._parse_analysis(analysis_text)

        except Exception as e:
            logger.error(f"Error analyzing fit: {e}")
            return {
                'match_score': 0,
                'strengths': [],
                'gaps': [],
                'strategies': []
            }

    def _build_analysis_prompt(self, resume: str, job_posting: Dict) -> str:
        """Build prompt for fit analysis"""
        company = job_posting.get('company', 'the company')
        position = job_posting.get('position', 'this position')
        requirements = job_posting.get('requirements', [])
        qualifications = job_posting.get('qualifications', [])

        requirements_text = '\n'.join(f"- {req}" for req in requirements) if requirements else "Not specified"
        qualifications_text = '\n'.join(f"- {qual}" for qual in qualifications) if qualifications else "Not specified"

        prompt = f"""You are a career counselor analyzing how well a candidate fits a job position.

JOB DETAILS:
Company: {company}
Position: {position}

Required Qualifications:
{requirements_text}

Preferred Qualifications:
{qualifications_text}

CANDIDATE'S RESUME:
{resume}

TASK:
Analyze the candidate's fit for this position. Provide your analysis in the following format:

MATCH SCORE: [0-100]

STRENGTHS:
- [List 3-5 key strengths/matches]

GAPS:
- [List any missing qualifications or gaps]

STRATEGIES TO ADDRESS GAPS:
- [Suggest 3-5 strategies to overcome gaps and make a strong impression]

APPLICATION TIPS:
- [Provide 2-3 specific tips for this application]

Be honest but constructive. Focus on actionable advice."""

        return prompt

    def _parse_analysis(self, analysis_text: str) -> Dict:
        """Parse analysis text into structured format"""
        import re

        result = {
            'match_score': 0,
            'strengths': [],
            'gaps': [],
            'strategies': [],
            'tips': [],
            'full_analysis': analysis_text
        }

        # Extract match score
        score_match = re.search(r'MATCH SCORE:\s*(\d+)', analysis_text)
        if score_match:
            result['match_score'] = int(score_match.group(1))

        # Extract sections
        sections = {
            'strengths': r'STRENGTHS:(.*?)(?=GAPS:|STRATEGIES:|$)',
            'gaps': r'GAPS:(.*?)(?=STRATEGIES:|APPLICATION TIPS:|$)',
            'strategies': r'STRATEGIES TO ADDRESS GAPS:(.*?)(?=APPLICATION TIPS:|$)',
            'tips': r'APPLICATION TIPS:(.*?)$'
        }

        for key, pattern in sections.items():
            match = re.search(pattern, analysis_text, re.DOTALL | re.IGNORECASE)
            if match:
                section_text = match.group(1)
                # Extract bullet points
                items = re.findall(r'[-•]\s*(.+?)(?=\n[-•]|\n\n|\Z)', section_text, re.DOTALL)
                result[key] = [item.strip() for item in items]

        return result
