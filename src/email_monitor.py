"""
Email monitoring module using Gmail API
Monitors inbox for job posting emails
"""

import os
import base64
import pickle
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import logging

logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class EmailMonitor:
    """Monitor Gmail inbox for job posting emails"""

    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.pickle'):
        """
        Initialize email monitor

        Args:
            credentials_path: Path to Gmail API credentials
            token_path: Path to save/load authentication token
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Load existing token if available
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Gmail credentials not found at {self.credentials_path}. "
                        "Please download from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Successfully authenticated with Gmail API")

    def get_unread_emails(self, labels: List[str] = None, max_results: int = 10) -> List[Dict]:
        """
        Get unread emails from inbox

        Args:
            labels: Gmail labels to filter by (e.g., ['INBOX', 'UNREAD'])
            max_results: Maximum number of emails to retrieve

        Returns:
            List of email dictionaries with id, subject, sender, body
        """
        try:
            query_parts = []
            if labels:
                query_parts.extend([f'label:{label}' for label in labels])
            else:
                query_parts.append('is:unread')

            query = ' '.join(query_parts)

            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])

            emails = []
            for message in messages:
                email_data = self._get_email_data(message['id'])
                if email_data:
                    emails.append(email_data)

            logger.info(f"Retrieved {len(emails)} unread emails")
            return emails

        except Exception as e:
            logger.error(f"Error retrieving emails: {e}")
            return []

    def _get_email_data(self, message_id: str) -> Optional[Dict]:
        """
        Get detailed email data

        Args:
            message_id: Gmail message ID

        Returns:
            Dictionary with email details
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')

            # Extract email body
            body = self._get_email_body(message['payload'])

            return {
                'id': message_id,
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body,
                'snippet': message.get('snippet', '')
            }

        except Exception as e:
            logger.error(f"Error getting email data for {message_id}: {e}")
            return None

    def _get_email_body(self, payload: Dict) -> str:
        """
        Extract email body from payload

        Args:
            payload: Email payload from Gmail API

        Returns:
            Email body text
        """
        body = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif 'parts' in part:
                    body = self._get_email_body(part)
                    if body:
                        break
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        return body

    def mark_as_read(self, message_id: str):
        """
        Mark email as read

        Args:
            message_id: Gmail message ID
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logger.info(f"Marked email {message_id} as read")
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")

    def get_email_by_id(self, message_id: str) -> Optional[Dict]:
        """
        Get specific email by ID

        Args:
            message_id: Gmail message ID

        Returns:
            Email data dictionary
        """
        return self._get_email_data(message_id)

    def search_emails(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search emails with custom query

        Args:
            query: Gmail search query
            max_results: Maximum results to return

        Returns:
            List of matching emails
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])

            emails = []
            for message in messages:
                email_data = self._get_email_data(message['id'])
                if email_data:
                    emails.append(email_data)

            return emails

        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []
