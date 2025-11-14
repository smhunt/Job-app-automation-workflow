#!/usr/bin/env python3
"""
Job Application Automation System
Main script to process job posting emails and generate customized applications
"""

import os
import sys
import argparse
import time
import logging
from typing import Optional

from src.email_monitor import EmailMonitor
from src.job_parser import JobParser
from src.ai_customizer import AICustomizer
from src.openai_customizer import OpenAICustomizer
from src.gap_analyzer import GapAnalyzer
from src.package_generator import PackageGenerator
from src.utils import (
    setup_logging,
    load_config,
    load_template,
    validate_config,
    ensure_directories,
    create_default_config
)

logger = logging.getLogger(__name__)


class JobApplicationAutomation:
    """Main automation orchestrator"""

    def __init__(self, config_path: str = 'config.yml'):
        """
        Initialize automation system

        Args:
            config_path: Path to configuration file
        """
        # Load and validate configuration
        self.config = load_config(config_path)
        validate_config(self.config)
        ensure_directories(self.config)

        # Setup logging
        log_config = self.config.get('logging', {})
        setup_logging(
            log_level=log_config.get('level', 'INFO'),
            log_file=log_config.get('file')
        )

        # Initialize components
        self.email_monitor = EmailMonitor()
        self.job_parser = JobParser()

        # Initialize AI provider based on config
        provider = self.config['api'].get('provider', 'anthropic').lower()
        if provider == 'openai':
            use_batch = self.config['api'].get('use_batch', False)
            model = self.config['api'].get('openai_model', 'gpt-4o')
            self.ai_customizer = OpenAICustomizer(
                api_key=self.config['api'].get('openai_key'),
                use_batch=use_batch
            )
            self.ai_customizer.model = model
            mode = "batch (50% off)" if use_batch else "real-time"
            logger.info(f"Using OpenAI provider: {model} in {mode} mode")
        else:
            self.ai_customizer = AICustomizer(
                api_key=self.config['api'].get('anthropic_key')
            )
            logger.info("Using Anthropic provider (Claude)")

        self.gap_analyzer = GapAnalyzer()
        self.package_generator = PackageGenerator(
            output_dir=self.config['output']['directory']
        )

        # Load templates
        self.resume_template = load_template(self.config['templates']['resume'])
        self.cover_letter_template = load_template(
            self.config['templates']['cover_letter']
        )

        logger.info("Job Application Automation System initialized")

    def process_email(self, email_data: dict) -> Optional[dict]:
        """
        Process a single job posting email

        Args:
            email_data: Email data dictionary

        Returns:
            Dictionary with generated file paths
        """
        logger.info(f"Processing email: {email_data.get('subject', 'No subject')}")

        # Check if it's a job posting
        if not self.job_parser.is_job_posting(email_data):
            logger.info("Email does not appear to be a job posting, skipping")
            return None

        # Parse job posting
        job_posting = self.job_parser.parse(email_data)
        logger.info(f"Parsed job: {job_posting.company} - {job_posting.position}")

        # Analyze fit
        logger.info("Analyzing candidate fit...")
        analysis = self.ai_customizer.analyze_fit(
            self.resume_template,
            job_posting.to_dict()
        )

        # Customize resume
        logger.info("Customizing resume...")
        customized_resume = self.ai_customizer.customize_resume(
            self.resume_template,
            job_posting.to_dict()
        )

        # Generate cover letter
        logger.info("Generating cover letter...")
        cover_letter = self.ai_customizer.customize_cover_letter(
            self.cover_letter_template,
            job_posting.to_dict(),
            self.resume_template
        )

        # Generate analysis report
        logger.info("Generating analysis report...")
        analysis_report = self.gap_analyzer.generate_report(
            job_posting.to_dict(),
            analysis,
            customized_resume,
            cover_letter
        )

        # Generate package
        logger.info("Generating application package...")
        files = self.package_generator.generate_package(
            job_posting.to_dict(),
            customized_resume,
            cover_letter,
            analysis_report
        )

        # Create quick summary
        quick_summary = self.gap_analyzer.create_quick_summary(
            analysis,
            job_posting.to_dict()
        )

        # Create application guide
        summary_path = self.package_generator.create_application_summary(
            files,
            job_posting.to_dict(),
            quick_summary
        )

        # Mark email as processed
        if 'id' in email_data:
            self.email_monitor.mark_as_read(email_data['id'])

        logger.info(f"✓ Application package generated successfully!")
        logger.info(f"  Analysis report: {files.get('analysis_report')}")
        logger.info(f"  Application guide: {summary_path}")

        print("\n" + "="*70)
        print(quick_summary)
        print("="*70)
        print(f"\nApplication package saved to: {self.config['output']['directory']}")
        print(f"Review the application guide: {summary_path}\n")

        return {
            'files': files,
            'summary_path': summary_path,
            'analysis': analysis,
            'job_posting': job_posting.to_dict()
        }

    def monitor_inbox(self, interval: int = None):
        """
        Monitor inbox for new job postings

        Args:
            interval: Check interval in seconds (default from config)
        """
        if interval is None:
            interval = self.config['email'].get('check_interval', 300)

        logger.info(f"Starting inbox monitoring (checking every {interval} seconds)")
        print(f"Monitoring {self.config['email']['address']} for job postings...")
        print(f"Checking every {interval} seconds. Press Ctrl+C to stop.\n")

        processed_ids = set()

        try:
            while True:
                try:
                    # Get unread emails
                    labels = self.config['email'].get('labels', ['INBOX'])
                    emails = self.email_monitor.get_unread_emails(
                        labels=labels,
                        max_results=10
                    )

                    # Process new emails
                    for email_data in emails:
                        email_id = email_data.get('id')
                        if email_id not in processed_ids:
                            print(f"\nNew email detected: {email_data.get('subject')}")
                            result = self.process_email(email_data)
                            if result:
                                processed_ids.add(email_id)
                            else:
                                logger.info("Not a job posting, skipped")

                    # Wait before next check
                    time.sleep(interval)

                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.error(f"Error during monitoring: {e}")
                    time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\nStopping inbox monitoring...")
            logger.info("Inbox monitoring stopped by user")

    def process_email_by_id(self, email_id: str):
        """
        Process specific email by ID

        Args:
            email_id: Gmail message ID
        """
        logger.info(f"Fetching email {email_id}")
        email_data = self.email_monitor.get_email_by_id(email_id)

        if not email_data:
            logger.error(f"Could not fetch email {email_id}")
            return

        self.process_email(email_data)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Job Application Automation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Monitor inbox continuously
  python main.py --monitor

  # Process specific email by ID
  python main.py --email-id <message-id>

  # Create default config file
  python main.py --create-config

  # Monitor with custom interval (seconds)
  python main.py --monitor --interval 600
        """
    )

    parser.add_argument(
        '--monitor',
        action='store_true',
        help='Monitor inbox for new job postings'
    )

    parser.add_argument(
        '--email-id',
        type=str,
        help='Process specific email by ID'
    )

    parser.add_argument(
        '--interval',
        type=int,
        help='Monitoring interval in seconds (default: 300)'
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config.yml',
        help='Path to configuration file (default: config.yml)'
    )

    parser.add_argument(
        '--create-config',
        action='store_true',
        help='Create default configuration file'
    )

    args = parser.parse_args()

    # Create default config if requested
    if args.create_config:
        create_default_config()
        return

    # Check if config exists
    if not os.path.exists(args.config):
        print(f"Error: Configuration file not found: {args.config}")
        print("\nCreate a default configuration with:")
        print("  python main.py --create-config")
        print("\nThen copy and edit it:")
        print("  cp config.example.yml config.yml")
        sys.exit(1)

    try:
        # Initialize automation system
        automation = JobApplicationAutomation(args.config)

        # Execute requested action
        if args.monitor:
            automation.monitor_inbox(interval=args.interval)
        elif args.email_id:
            automation.process_email_by_id(args.email_id)
        else:
            parser.print_help()
            print("\nNo action specified. Use --monitor or --email-id")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nPlease ensure all required files are in place:")
        print("  - config.yml (configuration)")
        print("  - credentials.json (Gmail API credentials)")
        print("  - templates/resume.txt (your resume)")
        print("  - templates/cover_letter_template.txt (cover letter template)")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
