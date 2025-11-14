"""
Application package generator
Creates formatted output files (PDF, DOCX, etc.)
"""

import os
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PackageGenerator:
    """Generate application package files"""

    def __init__(self, output_dir: str = 'output'):
        """
        Initialize package generator

        Args:
            output_dir: Directory to save generated files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_package(self, job_posting: Dict, resume: str,
                        cover_letter: str, analysis_report: str) -> Dict[str, str]:
        """
        Generate complete application package

        Args:
            job_posting: Job posting data
            resume: Customized resume text
            cover_letter: Customized cover letter text
            analysis_report: Analysis report markdown

        Returns:
            Dictionary with file paths
        """
        company = self._sanitize_filename(job_posting.get('company', 'Unknown'))
        position = self._sanitize_filename(job_posting.get('position', 'Unknown'))
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        base_name = f"{company}_{position}_{timestamp}"

        files = {}

        # Save resume as text
        resume_path = os.path.join(self.output_dir, f"{base_name}_resume.txt")
        with open(resume_path, 'w', encoding='utf-8') as f:
            f.write(resume)
        files['resume_txt'] = resume_path
        logger.info(f"Saved resume to {resume_path}")

        # Save cover letter
        cover_letter_path = os.path.join(self.output_dir, f"{base_name}_cover_letter.txt")
        with open(cover_letter_path, 'w', encoding='utf-8') as f:
            f.write(cover_letter)
        files['cover_letter_txt'] = cover_letter_path
        logger.info(f"Saved cover letter to {cover_letter_path}")

        # Save analysis report
        report_path = os.path.join(self.output_dir, f"{base_name}_analysis.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(analysis_report)
        files['analysis_report'] = report_path
        logger.info(f"Saved analysis report to {report_path}")

        # Try to generate PDF versions if possible
        try:
            pdf_files = self._generate_pdfs(base_name, resume, cover_letter)
            files.update(pdf_files)
        except Exception as e:
            logger.warning(f"Could not generate PDFs: {e}")

        # Save job details as JSON for reference
        import json
        job_details_path = os.path.join(self.output_dir, f"{base_name}_job_details.json")
        with open(job_details_path, 'w', encoding='utf-8') as f:
            json.dump(job_posting, f, indent=2, default=str)
        files['job_details'] = job_details_path

        return files

    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize filename to remove invalid characters

        Args:
            name: Original name

        Returns:
            Sanitized filename
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')

        # Limit length
        name = name[:50]

        # Remove extra spaces
        name = '_'.join(name.split())

        return name

    def _generate_pdfs(self, base_name: str, resume: str, cover_letter: str) -> Dict[str, str]:
        """
        Generate PDF versions of documents

        Args:
            base_name: Base filename
            resume: Resume text
            cover_letter: Cover letter text

        Returns:
            Dictionary with PDF file paths
        """
        pdf_files = {}

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch

            styles = getSampleStyleSheet()

            # Generate resume PDF
            resume_pdf_path = os.path.join(self.output_dir, f"{base_name}_resume.pdf")
            doc = SimpleDocTemplate(resume_pdf_path, pagesize=letter)
            story = []

            # Add resume content
            for line in resume.split('\n'):
                if line.strip():
                    para = Paragraph(line, styles['Normal'])
                    story.append(para)
                    story.append(Spacer(1, 0.1 * inch))

            doc.build(story)
            pdf_files['resume_pdf'] = resume_pdf_path
            logger.info(f"Generated PDF resume: {resume_pdf_path}")

            # Generate cover letter PDF
            cover_letter_pdf_path = os.path.join(self.output_dir, f"{base_name}_cover_letter.pdf")
            doc = SimpleDocTemplate(cover_letter_pdf_path, pagesize=letter)
            story = []

            for line in cover_letter.split('\n'):
                if line.strip():
                    para = Paragraph(line, styles['Normal'])
                    story.append(para)
                    story.append(Spacer(1, 0.1 * inch))

            doc.build(story)
            pdf_files['cover_letter_pdf'] = cover_letter_pdf_path
            logger.info(f"Generated PDF cover letter: {cover_letter_pdf_path}")

        except ImportError:
            logger.warning("reportlab not installed, skipping PDF generation")
        except Exception as e:
            logger.error(f"Error generating PDFs: {e}")

        return pdf_files

    def create_application_summary(self, files: Dict[str, str],
                                   job_posting: Dict,
                                   quick_summary: str) -> str:
        """
        Create summary document with easy application instructions

        Args:
            files: Dictionary of generated file paths
            job_posting: Job posting data
            quick_summary: Quick summary text

        Returns:
            Path to summary file
        """
        company = job_posting.get('company', 'Unknown')
        position = job_posting.get('position', 'Unknown')

        summary = f"""# Application Package Ready: {company} - {position}

{quick_summary}

## Generated Files

"""
        for file_type, file_path in files.items():
            summary += f"- **{file_type.replace('_', ' ').title()}:** `{file_path}`\n"

        summary += "\n## How to Apply\n\n"

        if job_posting.get('application_url'):
            summary += f"""### Online Application
1. Visit: {job_posting['application_url']}
2. Upload your customized resume: `{files.get('resume_txt', 'resume.txt')}`
3. Upload your cover letter: `{files.get('cover_letter_txt', 'cover_letter.txt')}`
4. Fill in any additional required fields
5. Submit your application

"""

        if job_posting.get('application_email'):
            summary += f"""### Email Application
1. Compose email to: {job_posting['application_email']}
2. Subject: "Application for {position}"
3. Attach your resume and cover letter
4. Include a brief message referencing the position
5. Send

"""

        summary += f"""## Before You Apply

- [ ] Review all customized documents
- [ ] Research {company} (recent news, culture, values)
- [ ] Prepare examples for your key strengths
- [ ] Have a plan to address identified gaps
- [ ] Proofread all materials one final time

## Analysis Report

Review the detailed analysis report for:
- Complete gap analysis
- Specific strategies to stand out
- Application tips tailored to this role

**Report location:** `{files.get('analysis_report', 'analysis.md')}`

---

Good luck with your application!
"""

        # Save summary
        base_name = os.path.basename(files.get('resume_txt', 'application')).replace('_resume.txt', '')
        summary_path = os.path.join(self.output_dir, f"{base_name}_APPLICATION_GUIDE.md")

        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)

        logger.info(f"Created application summary: {summary_path}")
        return summary_path
