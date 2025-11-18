"""Notification utilities for alerts and monitoring."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import settings
from utils.logger import logger
from typing import Optional


class EmailNotifier:
    """Send email notifications."""

    def __init__(self):
        """Initialize email notifier."""
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.recipient = settings.NOTIFY_EMAIL

    def send_email(
        self,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send an email notification.

        Args:
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body

        Returns:
            bool: True if sent successfully
        """
        if not self.recipient:
            logger.warning("No notification email configured, skipping email")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.recipient
            msg['To'] = self.recipient

            # Attach text body
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)

            # Attach HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                # Note: Add authentication if needed
                # server.login(username, password)
                server.send_message(msg)

            logger.info(f"Email notification sent: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def notify_scraping_complete(self, results: dict) -> bool:
        """
        Send notification when scraping completes.

        Args:
            results: Scraping results dictionary

        Returns:
            bool: True if sent successfully
        """
        subject = f"PhilGEPS Scraping Complete - {results['new_records']} new records"

        body = f"""
PhilGEPS Scraping Session Complete

Status: {'Success' if results['success'] else 'Failed'}
Duration: {results['duration_seconds']:.2f} seconds
Total Scraped: {results['total_scraped']}
New Records: {results['new_records']}
Errors: {results['errors']}
Start Time: {results['start_time']}
End Time: {results['end_time']}
        """.strip()

        html_body = f"""
        <html>
        <body>
            <h2>PhilGEPS Scraping Session Complete</h2>
            <table style="border-collapse: collapse;">
                <tr><td style="padding: 8px;"><strong>Status:</strong></td><td style="padding: 8px;">{'✓ Success' if results['success'] else '✗ Failed'}</td></tr>
                <tr><td style="padding: 8px;"><strong>Duration:</strong></td><td style="padding: 8px;">{results['duration_seconds']:.2f} seconds</td></tr>
                <tr><td style="padding: 8px;"><strong>Total Scraped:</strong></td><td style="padding: 8px;">{results['total_scraped']}</td></tr>
                <tr><td style="padding: 8px;"><strong>New Records:</strong></td><td style="padding: 8px;">{results['new_records']}</td></tr>
                <tr><td style="padding: 8px;"><strong>Errors:</strong></td><td style="padding: 8px;">{results['errors']}</td></tr>
                <tr><td style="padding: 8px;"><strong>Start Time:</strong></td><td style="padding: 8px;">{results['start_time']}</td></tr>
                <tr><td style="padding: 8px;"><strong>End Time:</strong></td><td style="padding: 8px;">{results['end_time']}</td></tr>
            </table>
        </body>
        </html>
        """

        return self.send_email(subject, body, html_body)

    def notify_error(self, error_message: str) -> bool:
        """
        Send error notification.

        Args:
            error_message: Error description

        Returns:
            bool: True if sent successfully
        """
        subject = "PhilGEPS Scraper Error Alert"
        body = f"An error occurred in the PhilGEPS scraper:\n\n{error_message}"

        return self.send_email(subject, body)
