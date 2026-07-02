"""Tests for the analytics module."""
from __future__ import annotations

import pytest
from scripts.analytics import format_text, format_markdown


class TestFormatText:
    def test_basic_format(self):
        report = {
            "period_hours": 24,
            "generated_at": "2025-01-01T00:00:00Z",
            "tokens": {
                "total_tokens": 1000,
                "input_tokens": 500,
                "output_tokens": 500,
                "estimated_cost_usd": 0.005,
                "requests": 10,
            },
            "tickets": {
                "total": 5,
                "by_status": {"open": 3, "closed": 2},
                "resolution_rate": 40.0,
            },
            "sessions": {
                "total_sessions": 20,
                "active_sessions": 5,
                "avg_messages_per_session": 3.5,
                "avg_duration_minutes": 15.0,
            },
            "rate_limits": {"rate_limit_hits": 2},
            "top_issues": [
                {"category": "password_reset", "count": 10},
                {"category": "billing", "count": 5},
            ],
        }
        output = format_text(report)
        assert "Helpdesk Analytics" in output
        assert "1,000" in output
        assert "password_reset" in output
        assert "billing" in output

    def test_empty_top_issues(self):
        report = {
            "period_hours": 24,
            "generated_at": "2025-01-01T00:00:00Z",
            "tokens": {
                "total_tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost_usd": 0.0,
                "requests": 0,
            },
            "tickets": {
                "total": 0,
                "by_status": {},
                "resolution_rate": 0.0,
            },
            "sessions": {
                "total_sessions": 0,
                "active_sessions": 0,
                "avg_messages_per_session": 0.0,
                "avg_duration_minutes": 0.0,
            },
            "rate_limits": {"rate_limit_hits": 0},
            "top_issues": [],
        }
        output = format_text(report)
        assert "Helpdesk Analytics" in output
        assert "Top Issues" not in output


class TestFormatMarkdown:
    def test_basic_format(self):
        report = {
            "period_hours": 24,
            "generated_at": "2025-01-01T00:00:00Z",
            "tokens": {
                "total_tokens": 1000,
                "input_tokens": 500,
                "output_tokens": 500,
                "estimated_cost_usd": 0.005,
                "requests": 10,
            },
            "tickets": {
                "total": 5,
                "by_status": {"open": 3, "closed": 2},
                "resolution_rate": 40.0,
            },
            "sessions": {
                "total_sessions": 20,
                "active_sessions": 5,
                "avg_messages_per_session": 3.5,
                "avg_duration_minutes": 15.0,
            },
            "rate_limits": {"rate_limit_hits": 2},
            "top_issues": [
                {"category": "password_reset", "count": 10},
            ],
        }
        output = format_markdown(report)
        assert "# Helpdesk Analytics Report" in output
        assert "## Token Usage" in output
        assert "## Tickets" in output
        assert "## Sessions" in output
        assert "## Rate Limiting" in output
        assert "## Top Issues" in output
        assert "password_reset" in output
