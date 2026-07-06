# SECURITY_REPORT.md — J1-PIPELINE Phase 3 (GUARDIAN)

**Repository:** `OneByJorah/CommandDesk`
**Analysis Date:** 2026-07-05
**Analyst:** J1-PIPELINE GUARDIAN
**Status:** DEGRADED — 2 critical, 3 degraded findings

---

## Security Score: 72/100

| Category | Score | Status |
|----------|-------|--------|
| Authentication | 80 | OK |
| Authorization | 85 | OK |
| HTTPS/TLS | 60 | DEGRADED |
| CSP/Headers | 85 | OK |
| Docker Hardening | 65 | DEGRADED |
| Secrets Management | 80 | OK |
| Rate Limiting | 70 | DEGRADED |
| Input Validation | 75 | OK |
| Audit Logging | 85 | OK |
| Supply Chain | 70 | DEGRADED |
| **Overall** | **72** | **DEGRADED** |

---

## 🔴 CRITICAL Security Findings

### S1. Rate Limiter Runtime Crash (C1 from AUDITOR)

**File:** `scripts/rate_limiter.py:39`
**Issue:** `self._sessions: dict[str, SessionState] =()` — empty tuple instead of empty dict. The rate limiter will crash on the first request with `AttributeError: 'tuple' object has no attribute 'get'`.

**Security Impact:** If the rate limiter crashes, the agent server returns a 500 error for all requests. This is a denial-of-service vulnerability — any request triggers the crash, taking down the entire helpdesk agent.

**Severity:** CRITICAL
**Fix:** Change `=()` to `={}`.

### S2. Missing `import requests` in Zammad Adapter (C4 from AUDITOR)

**File:** `ticket_platforms/zammad.py`
**Issue:** The Zammad adapter uses `requests.post()`, `requests.get()`, `requests.patch()` but never imports `requests`. Any ticket operation on Zammad will crash with `NameError`.

**Security Impact:** If Zammad is configured as the ticketing backend, all ticket operations fail silently or crash the agent. This is a reliability issue that could prevent legitimate support requests from being processed.

**Severity:** CRITICAL
**Fix:** Add `import requests` at the top of the file.

---

## 🟡 DEGRADED Security Findings

### S3. No HTTPS in Default Configuration

**Issue:** The Nginx config (`config/nginx.conf`) only listens on port 80 (HTTP). While the `setup.sh` script generates self-signed certificates, the Nginx config does not include an HTTPS server block. The `docker-compose.yml` maps ports 80 and 443, but only port 80 is configured.

**Impact:** All traffic between users and the helpdesk is unencrypted by default. Credentials, ticket data, and PII are transmitted in plaintext.

**Recommendation:** Add an HTTPS server block to `nginx.conf` that redirects HTTP to HTTPS and serves the self-signed certs from `certs/`.

### S4. Containers Run as Root

**Issue:** None of the Dockerfiles or docker-compose services specify a non-root user. All containers run as root by default.

**Impact:** If any container is compromised, the attacker has root access within that container. This increases the blast radius of a container breakout.

**Recommendation:** Add `USER` directives to Dockerfiles and `user:` directives to docker-compose services.

### S5. Unpinned Base Images

**Issue:** The Dockerfiles use `python:3.11-slim` without a specific patch version (e.g., `python:3.11.11-slim`). The `docker-compose.yml` uses `postgres:16-alpine` and `redis:7-alpine` without specific patch versions.

**Impact:** Base image updates could introduce breaking changes or security vulnerabilities without warning.

**Recommendation:** Pin all base images to specific SHA256 digests or at minimum specific patch versions.

### S6. ChromaDB Auth Token Default

**File:** `docker-compose.yml:143`
**Code:** `CHROMA_AUTH_TOKEN=${CHROMA_AUTH_TOKEN:-chromadb_token_change_me}`
**Issue:** The default ChromaDB auth token is `chromadb_token_change_me`, which is a weak default. If the user doesn't set `CHROMA_AUTH_TOKEN` in `.env`, the token is trivially guessable.

**Impact:** Anyone with network access to ChromaDB (port 8000) can query or modify the knowledge base.

**Recommendation:** Generate a random default token in `setup.sh` instead of using a hardcoded string.

### S7. n8n JWT Secret Default

**File:** `docker-compose.yml:202`
**Code:** `N8N_USER_MANAGEMENT_JWT_SECRET=${JWT_SECRET:-jwt_secret_change_me_please}`
**Issue:** Same pattern as S6 — hardcoded weak default.

**Impact:** If the JWT secret is not changed, an attacker could forge n8n authentication tokens.

---

## ✅ Security Strengths

### P1. Defense-in-Depth Architecture
- Nginx as security gateway (all external traffic goes through it)
- Rate limiting at 3 layers (Nginx zones, per-session, WhatsApp per-minute)
- IP whitelisting for admin routes (Docker subnet only)
- Security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, Referrer-Policy)

### P2. Content Filtering
PII detection and blocking for: passwords, credit card numbers, SSNs.

### P3. Audit Logging
All requests logged to PostgreSQL with session_id, user_id, action, details (JSONB), IP address, and timestamp.

### P4. Webhook Signature Verification
WhatsApp webhook uses HMAC-SHA256 signature verification (`X-Hub-Signature-256` header).

### P5. Secrets Management
- `.env` never committed (in `.gitignore`)
- Secrets directory (`.secrets/`) gitignored
- API keys passed via environment variables, not hardcoded
- Admin agent requires API key authentication

### P6. Security Audit History
Two dedicated security audit commits in git history:
- `5c7db2d` — sanitize email references
- `68216b0` — redact exposed tailscale IPs and demo emails

### P7. CodeQL Scanning
CodeQL configured for Python, JavaScript, and TypeScript analysis on every push and weekly.

### P8. Request Size Limits
Nginx configured with `client_max_body_size 4k` to prevent large payload attacks.

### P9. Service Isolation
Each service runs in its own container with Docker networks isolating them from the host.

---

## Security Checklist

| Control | Status | Notes |
|---------|--------|-------|
| Authentication | ✅ | API keys for admin, webhook signature verification |
| Authorization | ✅ | Two-agent architecture, MCP permissions |
| HTTPS | ❌ | No HTTPS server block in Nginx config |
| CSP Headers | ✅ | CSP, HSTS, X-Frame-Options, X-Content-Type-Options |
| Docker Hardening | ❌ | Containers run as root, no `.dockerignore` |
| Secrets Management | ✅ | `.env` gitignored, env vars for secrets |
| Rate Limiting | ⚠️ | Broken in-memory rate limiter (C1) |
| Input Validation | ✅ | Content filtering, request size limits |
| Audit Logging | ✅ | All requests logged to PostgreSQL |
| Supply Chain | ⚠️ | Dependabot configured but npm ecosystem mismatch |
| SBOM | ❌ | No SBOM generation |
| AppArmor/SELinux | ❌ | Not configured |
| Container Non-Root | ❌ | All containers run as root |

---

## Recommendations (Priority Order)

1. **CRITICAL:** Fix rate limiter tuple→dict bug (S1)
2. **CRITICAL:** Add `import requests` to Zammad adapter (S2)
3. **HIGH:** Add HTTPS server block to Nginx config (S3)
4. **HIGH:** Add non-root users to Dockerfiles (S4)
5. **MEDIUM:** Pin base images to specific versions (S5)
6. **MEDIUM:** Generate random ChromaDB auth token in setup.sh (S6)
7. **LOW:** Generate random n8n JWT secret in setup.sh (S7)
