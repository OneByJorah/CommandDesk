"""
Rate Limiter Middleware for Helpdesk Agent
Enforces per-session request limits and session duration.
"""
from __future__ import annotations

import time
import logging
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    max_requests_per_session: int = 50
    window_seconds: int = 3600
    max_message_length: int = 4000
    max_session_duration: int = 7200  # 2 hours


@dataclass
class SessionState:
    session_id: str
    user_id: str
    message_count: int = 0
    started_at: float = field(default_factory=time.time)
    last_request_at: float = field(default_factory=time.time)
    request_count: int = 0
    active: bool = True


class RateLimiter:
    """In-memory rate limiter with Redis persistence option."""

    def __init__(self, config: RateLimitConfig, redis_client=None):
        self.config = config
        self.redis = redis_client
        self._sessions: dict[str, SessionState] =()

    def check_request(self, session_id: str, user_id: str, message_length: int = 0) -> dict:
        """
        Check if a request is allowed.
        Returns: {"allowed": bool, "reason": str, "remaining": int}
        """
        now = time.time()

        # Get or create session
        state = self._sessions.get(session_id)
        if not state:
            state = SessionState(session_id=session_id, user_id=user_id)
            self._sessions[session_id] = state

        # Check session active
        if not state.active:
            return {"allowed": False, "reason": "Session expired or deactivated", "remaining": 0}

        # Check session duration
        session_age = now - state.started_at
        if session_age > self.config.max_session_duration:
            state.active = False
            return {
                "allowed": False,
                "reason": f"Session expired ({self.config.max_session_duration}s max)",
                "remaining": 0,
            }

        # Check message length
        if message_length > self.config.max_message_length:
            return {
                "allowed": False,
                "reason": f"Message too long ({message_length} > {self.config.max_message_length} chars)",
                "remaining": self.config.max_requests_per_session - state.request_count,
            }

        # Check rate limit (sliding window)
        window_start = now - self.config.window_seconds
        if state.last_request_at < window_start:
            # Reset window
            state.request_count = 1
        else:
            state.request_count += 1

        if state.request_count > self.config.max_requests_per_session:
            return {
                "allowed": False,
                "reason": f"Rate limit exceeded ({self.config.max_requests_per_session} req/{self.config.window_seconds}s)",
                "remaining": 0,
            }

        # Allowed
        state.message_count += 1
        state.last_request_at = now
        remaining = self.config.max_requests_per_session - state.request_count

        return {
            "allowed": True,
            "reason": "OK",
            "remaining": remaining,
            "session_remaining": int(self.config.max_session_duration - session_age),
        }

    def get_session_info(self, session_id: str) -> Optional[dict]:
        """Get current session info."""
        state = self._sessions.get(session_id)
        if not state:
            return None
        return {
            "session_id": state.session_id,
            "user_id": state.user_id,
            "message_count": state.message_count,
            "request_count": state.request_count,
            "active": state.active,
            "session_age_seconds": int(time.time() - state.started_at),
            "remaining_requests": max(0, self.config.max_requests_per_session - state.request_count),
        }

    def end_session(self, session_id: str):
        """End a session immediately."""
        state = self._sessions.get(session_id)
        if state:
            state.active = False

    def cleanup_expired(self):
        """Remove expired sessions from memory."""
        now = time.time()
        expired = [
            sid for sid, state in self._sessions.items()
            if not state.active or (now - state.started_at) > self.config.max_session_duration
        ]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)
