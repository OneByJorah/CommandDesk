"""Tests for the rate limiter module."""
from __future__ import annotations

import time
import pytest
from scripts.rate_limiter import RateLimiter, RateLimitConfig


@pytest.fixture
def config():
    return RateLimitConfig(
        max_requests_per_session=5,
        window_seconds=60,
        max_message_length=100,
        max_session_duration=300,
    )


@pytest.fixture
def limiter(config):
    return RateLimiter(config)


class TestRateLimitConfig:
    def test_default_values(self):
        cfg = RateLimitConfig()
        assert cfg.max_requests_per_session == 50
        assert cfg.window_seconds == 3600
        assert cfg.max_message_length == 4000
        assert cfg.max_session_duration == 7200


class TestRateLimiter:
    def test_initial_request_allowed(self, limiter):
        result = limiter.check_request("session1", "user1")
        assert result["allowed"] is True
        assert result["remaining"] == 4

    def test_rate_limit_exceeded(self, limiter):
        for i in range(5):
            result = limiter.check_request("session2", "user1")
            if i < 4:
                assert result["allowed"] is True, f"Request {i} should be allowed"
            else:
                assert result["allowed"] is False, f"Request {i} should be denied"
                assert "Rate limit exceeded" in result["reason"]

    def test_message_too_long(self, limiter):
        result = limiter.check_request("session3", "user1", message_length=200)
        assert result["allowed"] is False
        assert "too long" in result["reason"]

    def test_session_expired(self, config, limiter):
        # Create a session with very short duration
        short_config = RateLimitConfig(max_session_duration=0)
        short_limiter = RateLimiter(short_config)

        result = short_limiter.check_request("session4", "user1")
        assert result["allowed"] is False
        assert "expired" in result["reason"]

    def test_session_deactivated(self, limiter):
        limiter.check_request("session5", "user1")
        limiter.end_session("session5")
        result = limiter.check_request("session5", "user1")
        assert result["allowed"] is False
        assert "deactivated" in result["reason"]

    def test_get_session_info(self, limiter):
        limiter.check_request("session6", "user1")
        info = limiter.get_session_info("session6")
        assert info is not None
        assert info["session_id"] == "session6"
        assert info["user_id"] == "user1"
        assert info["message_count"] == 1
        assert info["active"] is True

    def test_get_session_info_nonexistent(self, limiter):
        info = limiter.get_session_info("nonexistent")
        assert info is None

    def test_cleanup_expired(self, config, limiter):
        # Create an expired session
        limiter.check_request("expired_session", "user1")
        # Manually set it to inactive
        limiter.end_session("expired_session")
        count = limiter.cleanup_expired()
        assert count >= 1

    def test_sliding_window_reset(self, config, limiter):
        """Test that the sliding window resets after the window period."""
        # Use a config with a very short window
        short_window = RateLimitConfig(
            max_requests_per_session=2,
            window_seconds=0,  # Window already expired
        )
        short_limiter = RateLimiter(short_window)

        # First request
        result = short_limiter.check_request("session7", "user1")
        assert result["allowed"] is True

        # Second request - window should reset since window_seconds=0
        result = short_limiter.check_request("session7", "user1")
        assert result["allowed"] is True

    def test_multiple_sessions_independent(self, limiter):
        """Test that different sessions have independent rate limits."""
        for i in range(5):
            limiter.check_request("session_a", "user1")

        # Session A should be exhausted
        result_a = limiter.check_request("session_a", "user1")
        assert result_a["allowed"] is False

        # Session B should still have all requests
        result_b = limiter.check_request("session_b", "user2")
        assert result_b["allowed"] is True
        assert result_b["remaining"] == 4
