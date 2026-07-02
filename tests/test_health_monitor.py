"""Tests for the health monitor module."""
from __future__ import annotations

import pytest
from scripts.health_monitor import check_service


class TestCheckService:
    @pytest.mark.asyncio
    async def test_service_no_url(self):
        result = await check_service("test-service", None)
        assert result["name"] == "test-service"
        assert result["status"] == "unknown"
        assert result["latency_ms"] == 0

    @pytest.mark.asyncio
    async def test_service_unreachable(self):
        result = await check_service("unreachable", "http://localhost:1/health")
        assert result["name"] == "unreachable"
        assert result["status"] == "unhealthy"
        assert "error" in result
