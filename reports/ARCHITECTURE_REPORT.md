# ARCHITECTURE_REPORT.md — J1-PIPELINE Phase 2 (ARCHITECT)

**Repository:** `OneByJorah/CommandDesk`
**Analysis Date:** 2026-07-05
**Analyst:** J1-PIPELINE ARCHITECT
**Status:** DEGRADED — 2 architectural concerns flagged

---

## Architecture Overview

CommandDesk uses a **microservices architecture** deployed via Docker Compose with 12+ containers. The architecture follows a layered pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                     External Channels                        │
│   WhatsApp (webhook) · Email (IMAP) · Web (chat widget)     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              Nginx Reverse Proxy (Security Gateway)          │
│   Rate Limiting · Security Headers · IP Whitelisting · TLS  │
└────┬────────────┬──────────────┬──────────────┬─────────────┘
     │            │              │              │
┌────▼───┐  ┌────▼───┐  ┌──────▼──────┐  ┌────▼──────────┐
│Helpdesk│  │ Admin  │  │   n8n       │  │   SearXNG     │
│ Agent  │  │ Agent  │  │ Workflows   │  │   Web Search  │
│ :8080  │  │ :8082  │  │ :5678       │  │   :8888       │
└───┬────┘  └───┬────┘  └──────┬──────┘  └───────┬───────┘
    │           │              │                  │
    └───────────┼──────────────┼──────────────────┘
                │              │
┌───────────────▼──────────────▼────────────────────────────┐
│                    Core Services                            │
│  ┌────────┐  ┌──────────┐  ┌────────┐  ┌──────────────┐  │
│  │ llama  │  │ ChromaDB │  │ Redis  │  │ PostgreSQL   │  │
│  │ :8081  │  │ :8000    │  │ :6379  │  │ :5432        │  │
│  └────────┘  └──────────┘  └────────┘  └──────────────┘  │
└───────────────────────────────────────────────────────────┘
```

---

## Architecture Score: 75/100

| Criterion | Score | Notes |
|-----------|-------|-------|
| Separation of Concerns | 85 | Good separation between agents, channels, and data |
| Service Boundaries | 80 | Well-defined service boundaries |
| Data Flow | 75 | Clear but some async patterns need work |
| Scalability | 60 | Redis-based sessions help, but agents are single-instance |
| Resilience | 65 | Health checks exist but no circuit breakers |
| Observability | 80 | Health monitor, analytics, audit logging |
| Security Architecture | 85 | Defense-in-depth: Nginx gateway, rate limiting, IP whitelist |
| **Overall** | **75** | **DEGRADED** |

---

## ✅ Strengths

### 1. Clean Adapter Pattern
The ticket platform adapter pattern (`ticket_platforms/`) is well-designed:
- Abstract base class (`Ticket` ABC) with 4 methods
- Decorator-based registry (`@register("name")`)
- Each adapter is self-contained (config, auth, API calls)
- Adding a new platform = write one class + register it

### 2. Two-Agent Security Architecture
Separating the helpdesk agent (restricted, no ticket creation) from the admin agent (full access) is a strong security pattern. This is enforced at:
- Config level (different YAML files)
- Environment level (`ALLOW_CREATE_TICKET=false` vs `true`)
- MCP permissions level (different allowed/denied tool lists)
- Nginx level (admin routes IP-whitelisted to Docker subnet)

### 3. Defense-in-Depth Security
- Nginx as security gateway (not just a reverse proxy)
- Rate limiting at 3 layers (Nginx zones, per-session, WhatsApp per-minute)
- Content filtering (PII patterns)
- Audit logging (all requests to PostgreSQL)
- Webhook signature verification (WhatsApp HMAC-SHA256)

### 4. Multi-Channel Support
WhatsApp (webhook + intent detection), Email (IMAP polling), and Web (chat widget + PWA) — all feeding into the same agent backend.

### 5. n8n Workflow Integration
Rather than building a custom workflow engine, the system delegates to n8n with 5 pre-built workflows covering the core automation needs.

---

## 🔴 Architectural Concerns

### A1. Single-Instance Agents (Scalability Risk)

**Issue:** Both `helpdesk-agent` and `admin-agent` are single instances. The `agent_server.py` runs with `--workers 2` (2 Uvicorn workers), but the in-memory rate limiter (`RateLimiter` class) stores session state in a Python dict — not in Redis. This means:

1. With multiple workers, each worker has its own in-memory rate limiter state
2. Rate limits are per-worker, not global
3. Session state is duplicated across workers

**Impact:** Rate limiting is ineffective with multiple workers. A user could exhaust their rate limit on one worker and switch to another.

**Recommendation:** Move rate limiter state to Redis (the `RateLimiter` class already has a `self.redis` field but doesn't use it for session storage — it uses `self._sessions` dict). The `SessionManager` class correctly uses Redis, but the `RateLimiter` does not.

### A2. Missing Circuit Breakers and Retry Logic

**Issue:** The system has no circuit breaker pattern for downstream dependencies:
- If `llama` (LLM) is down, the agent returns a generic error message
- If `chroma` (vector DB) is down, KB search fails silently
- If `postgres` is down, session persistence fails
- The `email_fetcher.py` has a basic retry loop but no exponential backoff

**Impact:** Cascading failures are possible. A single service outage can degrade the entire system.

**Recommendation:** Add circuit breakers (e.g., `pybreaker` or `aiobreaker`) for external service calls, with fallback behavior.

### A3. In-Memory Rate Limiter Not Using Redis

**Issue:** The `RateLimiter` class in `scripts/rate_limiter.py` accepts a `redis_client` parameter but only uses it for future persistence. All rate limit state is stored in `self._sessions: dict`. This means:
- Rate limits are lost on agent restart
- Rate limits don't work across multiple instances/workers
- No persistence of rate limit state

**Recommendation:** Implement Redis-backed rate limiting in the `RateLimiter` class, using the existing `self.redis` field.

---

## 🟡 Minor Concerns

### M1. WhatsApp Webhook Exposes Port 8383 to 0.0.0.0

**File:** `docker-compose.yml:349`
**Code:** `"0.0.0.0:8383:8383"`
**Issue:** The WhatsApp webhook exposes port 8383 to all interfaces (`0.0.0.0`), while all other services bind to `127.0.0.1`. This is necessary for WhatsApp to reach the webhook, but it's a larger attack surface.

**Note:** This is a necessary trade-off for webhook functionality. The webhook has signature verification (HMAC-SHA256) as a compensating control.

### M2. No Health Endpoint for Email Fetcher

**File:** `scripts/health_monitor.py:28`
**Code:** `"email-fetcher": None,  # No health endpoint, check process`
**Issue:** The email fetcher has no health endpoint, so the health monitor cannot check its status.

### M3. `docker-compose.yml` Uses Deprecated `version` Field

**File:** `docker-compose.yml:1`
**Code:** `version: "3.9"`
**Issue:** The `version` field is deprecated in Docker Compose v2 and should be removed.

---

## Data Flow Analysis

### Request Flow (Helpdesk Agent)

```
User → WhatsApp/Email/Web → Nginx → helpdesk-agent:8080
  → Rate Limiter (in-memory, broken with workers)
  → Session Manager (Redis)
  → LLM (llama.cpp via HTTP)
  → Response → Nginx → User
```

### Ticket Flow

```
External Ticketing System (osTicket/Freshdesk/Zammad)
  ←→ ticket_platforms/adapter.py (REST API)
  ←→ helpdesk-agent / admin-agent
```

### Knowledge Base Flow

```
knowledge-base/*.md → index_kb.py → ChromaDB (vector store)
  → Agent queries ChromaDB for semantic search
  → Returns relevant chunks
```

---

## Recommendations (Priority Order)

1. **CRITICAL:** Fix `RateLimiter` to use Redis-backed storage instead of in-memory dict
2. **HIGH:** Add circuit breakers for downstream service calls
3. **MEDIUM:** Add health endpoint to email-fetcher
4. **LOW:** Remove deprecated `version` field from docker-compose.yml
5. **LOW:** Add exponential backoff to email fetcher retry loop
