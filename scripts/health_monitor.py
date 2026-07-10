#!/usr/bin/env python3
"""
Health Monitoring Service
Collects metrics from all services and exposes them for the dashboard.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time

import httpx
import redis.asyncio as redis

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("health-monitor")

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

SERVICES = {
    "llama": "http://llama:8081/health",
    "helpdesk-agent": "http://helpdesk-agent:8080/health",
    "admin-agent": "http://admin-agent:8082/health",
    "chroma": "http://chroma:8000/api/v1/heartbeat",
    "searxng": "http://searxng:8080/search?q=test&format=json",
    "n8n": "http://n8n:5678/healthz",
    "email-fetcher": None,  # No health endpoint, check process
}


async def check_service(name: str, url: str | None) -> dict:
    """Check a single service health."""
    if not url:
        return {"name": name, "status": "unknown", "latency_ms": 0}

    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(url)
            latency = (time.time() - start) * 1000
            healthy = resp.status_code == 200
            return {
                "name": name,
                "status": "healthy" if healthy else "degraded",
                "latency_ms": round(latency, 1),
                "status_code": resp.status_code,
            }
    except Exception as e:
        latency = (time.time() - start) * 1000
        return {
            "name": name,
            "status": "unhealthy",
            "latency_ms": round(latency, 1),
            "error": str(e),
        }


async def collect_metrics(redis_client: redis.Redis) -> dict:
    """Collect all metrics."""
    # Service health checks
    results = []
    for name, url in SERVICES.items():
        result = await check_service(name, url)
        results.append(result)

    # Redis stats
    try:
        info = await redis_client.info("memory")
        redis_memory = info.get("used_memory_human", "unknown")
        redis_keys = await redis_client.dbsize()
    except Exception:
        redis_memory = "unknown"
        redis_keys = 0

    # Active sessions
    try:
        session_keys = await redis_client.keys("session:*")
        active_sessions = 0
        for key in session_keys:
            data = await redis_client.get(key)
            if data:
                session = json.loads(data)
                if session.get("active"):
                    active_sessions += 1
    except Exception:
        active_sessions = 0

    healthy_count = sum(1 for r in results if r.get("status") == "healthy")
    total_count = len(results)

    return {
        "timestamp": time.time(),
        "overall_status": "healthy" if healthy_count == total_count else "degraded" if healthy_count > total_count / 2 else "critical",
        "services": results,
        "summary": {
            "healthy": healthy_count,
            "total": total_count,
            "active_sessions": active_sessions,
            "redis_memory": redis_memory,
            "redis_keys": redis_keys,
        },
    }


async def run_monitor():
    """Main monitoring loop — stores metrics in Redis every 30s."""
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    logger.info("Health monitor started")

    while True:
        try:
            metrics = await collect_metrics(redis_client)
            # Store in Redis with 1-hour TTL
            await redis_client.setex("metrics:latest", 3600, json.dumps(metrics))
            logger.info(f"Metrics collected: {metrics['summary']}")
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")

        await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(run_monitor())
