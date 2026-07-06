# AUDIT_REPORT — CommandDesk

**Date:** 2026-07-05
**Auditor:** J1-PIPELINE (Phase 1 — AUDITOR)
**Status:** `DEGRADED` (Score: 74/100)

---

## 1. PROJECT CLASSIFICATION

| Field | Value |
|---|---|
| **Repo** | CommandDesk |
| **Class** | AI / Helpdesk / Full-Stack |
| **Primary Language** | Python 3.11 |
| **Framework** | FastAPI |
| **Deployment** | Docker Compose |
| **Tailscale Only** | No (exposed ports: 80, 443, 8383) |

---

## 2. README COMPLIANCE (README_STANDARD.md)

| Requirement | Status | Notes |
|---|---|---|
| One-line positioning | ✅ | "Self-Hosted AI Helpdesk Agent" |
| Max 3 badges | ❌ | Has **5 badges** (Python, FastAPI, Docker, AI, MIT) |
| 60-second quick start | ✅ | `git clone` → `cp .env.example .env` → `docker compose up -d` |
| Features (3-5 bullets) | ✅ | 8 features listed |
| Architecture diagram | ✅ | ASCII diagram present |
| Contributing section | ✅ | Links to CONTRIBUTING.md |
| License section | ✅ | MIT |

**Issue:** README has 5 badges — exceeds the 3-badge max per README_STANDARD.md.

---

## 3. CODE QUALITY — CRITICAL & DEGRADED ITEMS

### 🔴 CRITICAL (Must Fix)

| # | File | Issue | Severity |
|---|---|---|---|
| C1 | `rate_limiter.py:64` | **Bug:** `self._sessions: dict[str, SessionState] =()` — Empty tuple instead of dict `{}`. Causes `AttributeError` on first access. | CRITICAL |
| C2 | `zammad.py` | **Missing import:** Uses `requests.post()`, `requests.patch()`, `requests.get()` but `import requests` is missing. Will crash at runtime. | CRITICAL |
| C3 | `session_manager.py:38` | **SQL Injection:** `INTERVAL '{} seconds'".format(self.max_duration)` — Uses string formatting for SQL query parameter. | CRITICAL |
| C4 | `health_monitor.py:22` | **Wrong Redis URL:** `redis://redis:***@postgres:5432/helpdesk` — References PostgreSQL port (5432) instead of Redis port (6379), and uses `***` as password placeholder in a default. | CRITICAL |
| C5 | `whatsapp_webhook.py:29` | **Same wrong Redis URL:** `redis://redis:***@postgres:5432/helpdesk` | CRITICAL |
| C6 | `email_fetcher.py:83` | **Missing API endpoint:** POSTs to `/tickets/create` but no such route exists in `agent_server.py` — only `/chat` and `/health` are defined. Feature is broken. | CRITICAL |

### 🟡 DEGRADED (Should Fix)

| # | File | Issue | Severity |
|---|---|---|---|
| D1 | `rate_limiter.py` | **In-memory only:** Redis client is stored but never used. Rate limiting won't work across replicas/restarts. | DEGRADED |
| D2 | `agent_server.py` | **Blocking calls in async:** `get_system_prompt()` (file I/O) and `rate_limiter.check_request()` are sync methods called from async endpoints. | DEGRADED |
| D3 | `session_manager.py:92` | **O(N) `redis.keys()`:** Used in `get_active_count()` and `cleanup_expired()` — dangerous in production with many sessions. | DEGRADED |
| D4 | `health_monitor.py:83` | **O(N) `redis.keys()`:** Same pattern as D3. | DEGRADED |
| D5 | `analytics.py:10` | **Hardcoded password in URL:** `postgresql://helpdesk:***@postgres:5432/helpdesk` | DEGRADED |
| D6 | `whatsapp_webhook.py:138` | **Import inside function:** `import re` should be at module level. | DEGRADED |

---

## 4. SECURITY AUDIT (GUARDIAN — Phase 3 Preview)

| Check | Status | Notes |
|---|---|---|
| Default credentials | ❌ | `change_me` passwords throughout: JWT_SECRET, CHROMA_AUTH_TOKEN, WHATSAPP_WEBHOOK_SECRET, DB_PASSWORD, REDIS_PASSWORD |
| HTTPS enforced | ❌ | Nginx listens on port 80 only (no 443 config). `docker-compose.prod.yml` exposes 443 but no TLS certs configured. |
| CORS | ⚠️ | `allow_origins=["*"]` — acceptable for development, but not documented as such |
| Secrets in repo | ✅ | `.env` in `.gitignore`, `*.pem`, `*.key` excluded |
| Gitleaks clean | ✅ | No hardcoded secrets found in code |
| Rate limiting | ✅ | Nginx + app-level rate limiting implemented |
| Docker rootless | ⚠️ | No non-root user specified in Dockerfiles |
| Content-Security-Policy | ✅ | Set in nginx.conf |
| SBOM | ❌ | No SBOM (CycloneDX or SPDX) present |
| Security.md | ✅ | Present with contact + disclosure policy |
| Auth for admin | ⚠️ | `ADMIN_API_KEY` configured but no auth middleware seen in agent_server.py |

---

## 5. DOCKER STANDARD CHECK

| Check | Status | Notes |
|---|---|---|
| Health checks | ✅ | Defined for all services |
| Named volumes | ✅ | All volumes named |
| `.dockerignore` | ❌ | **Missing** — `.env`, `.git`, `node_modules` could leak into build context |
| Multi-stage builds | ❌ | Dockerfile is single-stage |
| Image version tags | ⚠️ | `searxng:latest`, `n8n:latest` — not pinned |
| Non-root user | ❌ | Root user used in all Dockerfiles |
| Tailscale pattern | ❌ | Not implemented |

---

## 6. GITHUB STANDARD CHECK

| Check | Status | Notes |
|---|---|---|
| Repo description | ✅ | Set |
| Topics | ⚠️ | Could add more specific topics |
| Branch protection | ⚠️ | Not verified (requires GH API) |
| CODEOWNERS | ❌ | **Missing** |
| Dependabot | ✅ | `.github/dependabot.yml` present |
| Issue templates | ✅ | Bug report + feature request |
| PR template | ✅ | Present |
| CI workflows | ✅ | CI + CodeQL workflows present |

---

## 7. MISSING STANDARD FILES

| File | Purpose | Status |
|---|---|---|
| `j1.yaml` | Pipeline registry metadata | ❌ Missing |
| `INTENT.md` | Engineering intent (Phase -1 ORACLE) | ❌ Missing |
| `.dockerignore` | Docker build context optimization | ❌ Missing |
| `CHANGELOG.md` | Release history | ❌ Missing |
| `CODEOWNERS` | PR ownership routing | ❌ Missing |
| `pyproject.toml` / `setup.py` | Python package metadata | ❌ Missing |

---

## 8. PRODUCTION SCORE

| Category | Weight | Score | Weighted |
|---|---|---|---|
| Security | 20% | 65 | 13.0 |
| Architecture | 15% | 75 | 11.25 |
| Documentation | 15% | 80 | 12.0 |
| Testing | 15% | 55 | 8.25 |
| Deployment | 10% | 78 | 7.8 |
| Automation | 10% | 82 | 8.2 |
| GitHub Quality | 10% | 85 | 8.5 |
| Branding | 5% | 85 | 4.25 |

**Total Score: 73.25 / 100 — `DEGRADED`** (threshold: 90)

---

## 9. RECOMMENDED ACTIONS

### Immediate (CRITICAL fixes):
1. Fix `self._sessions = {}` in `rate_limiter.py:64` (typo `()` → `{}`)
2. Add `import requests` to `zammad.py`
3. Fix SQL injection in `session_manager.py:38` — use parameterized query
4. Fix Redis URLs in `health_monitor.py` and `whatsapp_webhook.py` (port 6379, proper placeholder)
5. Add `/tickets/create` endpoint to `agent_server.py` or fix `email_fetcher.py` to use `/chat`

### Short-term:
6. Add `.dockerignore`
7. Pin Docker image versions (no `:latest`)
8. Fix blocking calls in async endpoints
9. Replace `redis.keys()` with `SCAN` in session_manager and health_monitor
10. Add `import re` at top of `whatsapp_webhook.py`

### Medium-term:
11. Create `j1.yaml` and `INTENT.md`
12. Create `CHANGELOG.md`
13. Add CODEOWNERS file
14. Implement Redis-backed rate limiting (not just in-memory)
15. Add non-root user to Dockerfiles
