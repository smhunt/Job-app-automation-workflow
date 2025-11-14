"""
OpenAI API integration module
Supports both real-time and batch (50% cheaper) processing
"""

import os
import json
import time
from typing import Dict, Optional, List
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class OpenAICustomizer:
    """OpenAI-powered resume and cover letter customizer"""

    def __init__(self, api_key: Optional[str] = None, use_batch: bool = False):
        """
        Initialize OpenAI customizer

        Args:
            api_key: OpenAI API key (or use OPENAI_API_KEY env var)
            use_batch: Use batch API for 50% cost savings (slower, 24hr processing)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")

        self.client = OpenAI(api_key=self.api_key)
        self.use_batch = use_batch
        self.model = "gpt-4o"  # Or gpt-4o-mini for even cheaper

        # Cost tracking (per 1M tokens)
        self.costs = {
            'gpt-4o': {'input': 2.50, 'output': 10.00},
            'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
            'gpt-4-turbo': {'input': 10.00, 'output': 30.00}
        }

        if use_batch:
            # Batch API is 50% cheaper
            self.costs = {k: {t: p * 0.5 for t, p in v.items()}
                         for k, v in self.costs.items()}

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

        if self.use_batch:
            logger.info("Batch mode enabled - job will be queued")
            return self._process_batch([{
                'type': 'resume',
                'prompt': prompt,
                'job': job_posting
            }])[0]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert resume writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            customized_resume = response.choices[0].message.content
            logger.info(f"Successfully customized resume for {job_posting.get('position', 'position')}")

            # Log cost
            self._log_cost(response.usage)

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

        if self.use_batch:
            logger.info("Batch mode enabled - job will be queued")
            return self._process_batch([{
                'type': 'cover_letter',
                'prompt': prompt,
                'job': job_posting
            }])[0]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert cover letter writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            cover_letter = response.choices[0].message.content
            logger.info(f"Successfully generated cover letter for {job_posting.get('position', 'position')}")

            self._log_cost(response.usage)

            return cover_letter

        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return template

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

        if self.use_batch:
            logger.info("Batch mode enabled - job will be queued")
            analysis_text = self._process_batch([{
                'type': 'analysis',
                'prompt': prompt,
                'job': job_posting
            }])[0]
            return self._parse_analysis(analysis_text)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a career counselor analyzing job fit."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )

            analysis_text = response.choices[0].message.content
            logger.info("Successfully analyzed job fit")

            self._log_cost(response.usage)

            return self._parse_analysis(analysis_text)

        except Exception as e:
            logger.error(f"Error analyzing fit: {e}")
            return {
                'match_score': 0,
                'strengths': [],
                'gaps': [],
                'strategies': []
            }

    def _process_batch(self, tasks: List[Dict]) -> List[str]:
        """
        Process tasks using OpenAI Batch API (50% cheaper, up to 24hr wait)

        Args:
            tasks: List of task dictionaries

        Returns:
            List of results
        """
        # Create JSONL file for batch
        batch_file_content = []
        for i, task in enumerate(tasks):
            batch_file_content.append({
                "custom_id": f"task-{i}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are an expert career advisor."},
                        {"role": "user", "content": task['prompt']}
                    ],
                    "max_tokens": 2000
                }
            })

        # Write to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for item in batch_file_content:
                f.write(json.dumps(item) + '\n')
            batch_file_path = f.name

        try:
            # Upload file
            with open(batch_file_path, 'rb') as f:
                batch_input_file = self.client.files.create(
                    file=f,
                    purpose="batch"
                )

            # Create batch job
            batch = self.client.batches.create(
                input_file_id=batch_input_file.id,
                endpoint="/v1/chat/completions",
                completion_window="24h"
            )

            logger.info(f"Batch job created: {batch.id}")
            logger.info("Waiting for batch to complete (this may take up to 24 hours)...")

            # Poll for completion
            while batch.status not in ['completed', 'failed', 'cancelled']:
                time.sleep(30)  # Check every 30 seconds
                batch = self.client.batches.retrieve(batch.id)
                logger.info(f"Batch status: {batch.status}")

            if batch.status == 'completed':
                # Download results
                result_file = self.client.files.content(batch.output_file_id)
                results = []
                for line in result_file.text.strip().split('\n'):
                    result = json.loads(line)
                    results.append(result['response']['body']['choices'][0]['message']['content'])

                logger.info("Batch processing completed successfully")
                return results
            else:
                logger.error(f"Batch processing failed: {batch.status}")
                raise Exception(f"Batch failed with status: {batch.status}")

        finally:
            # Cleanup temp file
            os.unlink(batch_file_path)

    def _build_resume_prompt(self, resume: str, job_posting: Dict) -> str:
        """Build prompt for resume customization"""
        company = job_posting.get('company', 'the company')
        position = job_posting.get('position', 'this position')
        requirements = job_posting.get('requirements', [])
        responsibilities = job_posting.get('responsibilities', [])

        requirements_text = '\n'.join(f"- {req}" for req in requirements) if requirements else "Not specified"
        responsibilities_text = '\n'.join(f"- {resp}" for resp in responsibilities) if responsibilities else "Not specified"

        return f"""You are an expert resume writer helping customize a resume for a specific job application.

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

    def _build_cover_letter_prompt(self, template: str, job_posting: Dict, resume: str) -> str:
        """Build prompt for cover letter generation"""
        company = job_posting.get('company', 'the company')
        position = job_posting.get('position', 'this position')
        description = job_posting.get('description', '')
        requirements = job_posting.get('requirements', [])

        requirements_text = '\n'.join(f"- {req}" for req in requirements) if requirements else "Not specified"

        return f"""You are an expert cover letter writer helping create a compelling cover letter for a job application.

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

1. Address the hiring manager professionally
2. Show genuine enthusiasm for the company and role
3. Highlight 2-3 key experiences that match job requirements
4. Explain why you're interested in this specific company
5. Be confident but not arrogant
6. Keep it concise (3-4 paragraphs, under 400 words)
7. End with a strong call to action
8. Match the tone of the template

Return ONLY the cover letter text, no additional commentary."""

    def _build_analysis_prompt(self, resume: str, job_posting: Dict) -> str:
        """Build prompt for fit analysis"""
        company = job_posting.get('company', 'the company')
        position = job_posting.get('position', 'this position')
        requirements = job_posting.get('requirements', [])
        qualifications = job_posting.get('qualifications', [])

        requirements_text = '\n'.join(f"- {req}" for req in requirements) if requirements else "Not specified"
        qualifications_text = '\n'.join(f"- {qual}" for qual in qualifications) if qualifications else "Not specified"

        return f"""You are a career counselor analyzing how well a candidate fits a job position.

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
                items = re.findall(r'[-•]\s*(.+?)(?=\n[-•]|\n\n|\Z)', section_text, re.DOTALL)
                result[key] = [item.strip() for item in items]

        return result

    def _log_cost(self, usage):
        """Log estimated cost for the API call"""
        if hasattr(usage, 'prompt_tokens') and hasattr(usage, 'completion_tokens'):
            input_cost = (usage.prompt_tokens / 1_000_000) * self.costs[self.model]['input']
            output_cost = (usage.completion_tokens / 1_000_000) * self.costs[self.model]['output']
            total_cost = input_cost + output_cost

            mode = "batch" if self.use_batch else "real-time"
            logger.info(f"API cost ({mode}): ${total_cost:.4f} "
                       f"(input: {usage.prompt_tokens}, output: {usage.completion_tokens})")

    def estimate_job_cost(self) -> Dict[str, float]:
        """
        Estimate cost per job application

        Returns:
            Dictionary with cost estimates
        """
        # Typical token usage per job
        typical_usage = {
            'analysis': {'input': 2000, 'output': 500},
            'resume': {'input': 2500, 'output': 1000},
            'cover_letter': {'input': 2000, 'output': 600}
        }

        costs = {}
        for task, tokens in typical_usage.items():
            input_cost = (tokens['input'] / 1_000_000) * self.costs[self.model]['input']
            output_cost = (tokens['output'] / 1_000_000) * self.costs[self.model]['output']
            costs[task] = input_cost + output_cost

        costs['total_per_job'] = sum(costs.values())
        costs['mode'] = 'batch (50% off)' if self.use_batch else 'real-time'

        return costs
