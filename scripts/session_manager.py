"""
Session Manager for Helpdesk Agent
Tracks active sessions in Redis with PostgreSQL persistence.
"""
from __future__ import annotations

import json
import logging
import time
import uuid

logger = logging.getLogger(__name__)


class SessionManager:
    """Manage user sessions with Redis cache and PostgreSQL persistence."""

    def __init__(self, redis_client, postgres_pool=None, max_duration: int = 7200):
        self.redis = redis_client
        self.pg_pool = postgres_pool
        self.max_duration = max_duration

    async def create_session(self, user_id: str, platform: str = "web", ip: str = None) -> dict:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        now = time.time()
        expires_at = now + self.max_duration

        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "platform": platform,
            "message_count": 0,
            "started_at": now,
            "expires_at": expires_at,
            "active": True,
            "ip": ip,
        }

        # Store in Redis
        key = f"session:{session_id}"
        await self.redis.setex(key, self.max_duration, json.dumps(session_data))

        # Store in PostgreSQL for persistence
        if self.pg_pool:
            async with self.pg_pool.acquire() as conn:
                await conn.execute(
                    """INSERT INTO sessions (id, user_id, platform, message_count, started_at, expires_at, active, ip_address)
                       VALUES ($1, $2, $3, $4, NOW(), NOW() + MAKE_INTERVAL(secs => $5), TRUE, $6::inet)""",
                    session_id, user_id, platform, 0, self.max_duration, ip,
                )

        return session_data

    async def get_session(self, session_id: str) -> dict | None:
        """Get session data."""
        key = f"session:{session_id}"
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def increment_message(self, session_id: str):
        """Increment message count."""
        key = f"session:{session_id}"
        data = await self.redis.get(key)
        if data:
            session = json.loads(data)
            session["message_count"] += 1
            ttl = await self.redis.ttl(key)
            if ttl > 0:
                await self.redis.setex(key, ttl, json.dumps(session))

    async def end_session(self, session_id: str):
        """End a session."""
        key = f"session:{session_id}"
        data = await self.redis.get(key)
        if data:
            session = json.loads(data)
            session["active"] = False
            await self.redis.setex(key, 300, json.dumps(session))  # Keep for 5 min for audit

        if self.pg_pool:
            async with self.pg_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE sessions SET active = FALSE WHERE id = $1",
                    session_id,
                )

    async def get_active_count(self) -> int:
        """Get count of active sessions using SCAN (avoid O(N) KEYS)."""
        count = 0
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor, match="session:*", count=1000)
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    session = json.loads(data)
                    if session.get("active"):
                        count += 1
            if cursor == 0:
                break
        return count

    async def cleanup_expired(self):
        """Remove expired sessions using SCAN (avoid O(N) KEYS)."""
        removed = 0
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor, match="session:*", count=1000)
            for key in keys:
                ttl = await self.redis.ttl(key)
                if ttl < 0:
                    await self.redis.delete(key)
                    removed += 1
            if cursor == 0:
                break
        return removed
