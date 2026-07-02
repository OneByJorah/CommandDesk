"""Tests for the email fetcher module."""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock
from scripts.email_fetcher import decode_mime_header, extract_email_body


class TestDecodeMimeHeader:
    def test_empty_header(self):
        assert decode_mime_header("") == ""

    def test_none_header(self):
        assert decode_mime_header(None) == ""

    def test_simple_ascii(self):
        result = decode_mime_header("Hello World")
        assert result == "Hello World"

    def test_encoded_header(self):
        """Test with a MIME encoded word."""
        from email.header import Header
        h = Header("Subject: Test", "utf-8")
        result = decode_mime_header(str(h))
        assert "Subject" in result
        assert "Test" in result


class TestExtractEmailBody:
    def test_simple_text_body(self):
        """Test extracting body from a simple email message."""
        from email.mime.text import MIMEText
        msg = MIMEText("This is a test body", "plain", "utf-8")
        body = extract_email_body(msg)
        assert body == "This is a test body"

    def test_multipart_body(self):
        """Test extracting body from a multipart message."""
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart("mixed")
        msg.attach(MIMEText("This is the plain text body", "plain", "utf-8"))
        msg.attach(MIMEText("<html><body>HTML body</body></html>", "html", "utf-8"))

        body = extract_email_body(msg)
        assert body == "This is the plain text body"

    def test_body_truncation(self):
        """Test that body is truncated at 10KB."""
        from email.mime.text import MIMEText
        long_text = "A" * 20000
        msg = MIMEText(long_text, "plain", "utf-8")
        body = extract_email_body(msg)
        assert len(body) == 10000

    def test_empty_body(self):
        """Test with an empty message body."""
        from email.mime.text import MIMEText
        msg = MIMEText("", "plain", "utf-8")
        body = extract_email_body(msg)
        assert body == ""
