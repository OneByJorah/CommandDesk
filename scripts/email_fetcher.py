#!/usr/bin/env python3
"""
Email Fetcher Service
Polls IMAP inbox and creates tickets via helpdesk agent API.
"""
from __future__ import annotations

import email
import imaplib
import json
import logging
import os
import time
import uuid
from email.header import decode_header
from typing import Optional

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("email_fetcher")

# Config
IMAP_HOST = os.getenv("IMAP_HOST", "")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
IMAP_USER = os.getenv("IMAP_USER", "")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD", "")
IMAP_FOLDER = os.getenv("IMAP_FOLDER", "INBOX")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))
TICKET_PLATFORM = os.getenv("TICKET_PLATFORM", "osticket")
HELPDESK_AGENT_URL = os.getenv("HELPDESK_AGENT_URL", "http://helpdesk-agent:8080")

# Optional: PostgreSQL for ticket caching
POSTGRES_URL = os.getenv("POSTGRES_URL", "")


def decode_mime_header(header_value: str) -> str:
    """Decode MIME encoded header."""
    if not header_value:
        return ""
    parts = decode_header(header_value)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return " ".join(decoded)


def extract_email_body(msg) -> str:
    """Extract plain text body from email message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                except Exception:
                    body = str(part.get_payload())
                break
    else:
        try:
            body = msg.get_payload(decode=True).decode("utf-8", errors="replace")
        except Exception:
            body = str(msg.get_payload())
    return body[:10000]  # Limit to 10KB


def process_email(mail: imaplib.IMAP4_SSL, num: str) -> Optional[dict]:
    """Process a single email and create ticket."""
    try:
        status, data = mail.fetch(num, "(RFC822)")
        if status != "OK":
            return None

        msg = email.message_from_bytes(data[0][1])
        subject = decode_mime_header(msg.get("Subject", "No Subject"))
        from_addr = decode_mime_header(msg.get("From", "unknown@unknown.com"))
        message_id = msg.get("Message-ID", str(uuid.uuid4()))
        body = extract_email_body(msg)

        # Extract email address
        email_addr = from_addr
        if "<" in from_addr and ">" in from_addr:
            email_addr = from_addr.split("<")[1].split(">")[0]

        logger.info(f"Processing email: {subject[:50]} from {email_addr}")

        # Create ticket via helpdesk agent API
        ticket_data = {
            "subject": subject,
            "body": body,
            "user_email": email_addr,
            "platform": TICKET_PLATFORM,
            "message_id": message_id,
        }

        with httpx.Client(timeout=30) as client:
            resp = client.post(f"{HELPDESK_AGENT_URL}/tickets/create", json=ticket_data)
            if resp.status_code == 200:
                result = resp.json()
                logger.info(f"Ticket created: {result.get('ticket_id')}")
                return result
            else:
                logger.warning(f"Ticket creation failed: {resp.status_code} {resp.text[:200]}")
                return None

    except Exception as e:
        logger.error(f"Error processing email {num}: {e}")
        return None


def poll_loop():
    """Main polling loop."""
    logger.info(f"Email fetcher started. Polling {IMAP_HOST}:{IMAP_PORT}/{IMAP_FOLDER} every {POLL_INTERVAL}s")

    while True:
        try:
            mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
            mail.login(IMAP_USER, IMAP_PASSWORD)
            mail.select(IMAP_FOLDER)

            # Search for unread emails
            status, messages = mail.search(None, "(UNSEEN)")
            if status == "OK" and messages[0]:
                email_ids = messages[0].split()
                logger.info(f"Found {len(email_ids)} unread emails")

                for num in email_ids:
                    result = process_email(mail, num)
                    if result:
                        # Mark as read
                        mail.store(num, "+FLAGS", "\\Seen")

            mail.logout()
            logger.info(f"Poll complete. Sleeping {POLL_INTERVAL}s...")

        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    if not IMAP_HOST or not IMAP_USER or not IMAP_PASSWORD:
        logger.error("IMAP_HOST, IMAP_USER, and IMAP_PASSWORD must be set")
        exit(1)
    poll_loop()
