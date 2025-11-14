"""
Utility functions for the job application automation system
"""

import os
import yaml
import logging
from typing import Dict, Any


def setup_logging(log_level: str = 'INFO', log_file: str = None):
    """
    Setup logging configuration

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    handlers = [logging.StreamHandler()]

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def load_config(config_path: str = 'config.yml') -> Dict[str, Any]:
    """
    Load configuration from YAML file

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    return config


def load_template(template_path: str) -> str:
    """
    Load template file

    Args:
        template_path: Path to template file

    Returns:
        Template content as string
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")

    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration

    Args:
        config: Configuration dictionary

    Returns:
        True if valid

    Raises:
        ValueError: If configuration is invalid
    """
    required_keys = ['email', 'api', 'templates', 'output']

    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")

    # Validate email config
    if 'address' not in config['email']:
        raise ValueError("Email address not configured")

    # Validate API config - check for at least one provider
    provider = config['api'].get('provider', 'anthropic').lower()

    if provider == 'anthropic':
        if 'anthropic_key' not in config['api'] or not config['api']['anthropic_key'] or config['api']['anthropic_key'] == 'your-anthropic-api-key-here':
            raise ValueError("Anthropic API key not configured or still has default value")
    elif provider == 'openai':
        if 'openai_key' not in config['api'] or not config['api']['openai_key'] or config['api']['openai_key'] == 'your-openai-api-key-here':
            raise ValueError("OpenAI API key not configured or still has default value")
    else:
        raise ValueError(f"Invalid API provider: {provider}. Must be 'anthropic' or 'openai'")

    # Validate template paths
    if 'resume' not in config['templates']:
        raise ValueError("Resume template path not configured")

    if 'cover_letter' not in config['templates']:
        raise ValueError("Cover letter template path not configured")

    return True


def create_default_config(output_path: str = 'config.example.yml'):
    """
    Create default configuration file

    Args:
        output_path: Path to save config file
    """
    default_config = {
        'email': {
            'address': 'sean.jobs@ecoworks.ca',
            'labels': ['INBOX'],
            'check_interval': 300  # seconds
        },
        'api': {
            'provider': 'openai',  # or 'anthropic'
            'anthropic_key': 'your-anthropic-api-key-here',
            'openai_key': 'your-openai-api-key-here',
            'openai_model': 'gpt-4o',
            'use_batch': False
        },
        'templates': {
            'resume': 'templates/resume.txt',
            'cover_letter': 'templates/cover_letter_template.txt'
        },
        'output': {
            'directory': 'output',
            'format': 'pdf'
        },
        'logging': {
            'level': 'INFO',
            'file': 'logs/job_automation.log'
        }
    }

    with open(output_path, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)

    print(f"Default configuration saved to {output_path}")


def ensure_directories(config: Dict[str, Any]):
    """
    Ensure required directories exist

    Args:
        config: Configuration dictionary
    """
    # Create output directory
    output_dir = config['output']['directory']
    os.makedirs(output_dir, exist_ok=True)

    # Create template directory
    template_dir = os.path.dirname(config['templates']['resume'])
    if template_dir:
        os.makedirs(template_dir, exist_ok=True)

    # Create log directory if specified
    if 'logging' in config and 'file' in config['logging']:
        log_dir = os.path.dirname(config['logging']['file'])
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
