# INTENT.md — J1-PIPELINE Phase -1 (ORACLE)

**Repository:** `OneByJorah/CommandDesk`
**Analysis Date:** 2026-07-05
**Analyst:** J1-PIPELINE ORACLE (read-only)
**Status:** Intent Reconstructed

---

## What This System Does

### Technical Role

CommandDesk is a **self-hosted, AI-powered helpdesk agent platform** that bridges local LLM inference with existing enterprise ticketing infrastructure. It is a complete, containerized stack that:

1. **Runs a local LLM** (Qwen2.5-7B-Instruct via llama.cpp, Q4_K_M GGUF, 65K context) for all AI operations — no external API calls, no data leaving the host.
2. **Connects to multiple ticketing backends** via a plug-in adapter architecture: osTicket (REST API v1), Freshdesk (REST API v2 + MCP protocol), and Zammad (REST API).
3. **Accepts support requests from multiple channels**: WhatsApp Business API (webhook with intent detection), Email/IMAP (polling with email-to-ticket conversion), and a web interface (chat widget + PWA).
4. **Provides two-tier AI agent access**:
   - **Helpdesk Agent** (port 8080) — restricted, end-user-facing. Can search/view/update/close the user's own tickets. Cannot create tickets.
   - **Admin Agent** (port 8082) — full-access, internal. Can create tickets, manage knowledge base, view analytics, check system health, manage all tickets across all users.
5. **Maintains a semantic knowledge base** via ChromaDB (all-MiniLM-L6-v2 embeddings, cosine similarity) for instant answer retrieval from markdown/text documents.
6. **Automates workflows** via n8n: smart ticket routing (keyword-based classification), auto-escalation, daily digests (weekdays 9AM), satisfaction surveys (every 4 hours), and ticket-created notifications.
7. **Enforces security** at every layer: rate limiting (per-session + per-IP + per-endpoint via Nginx zones), content filtering (PII patterns: password, credit_card, ssn), audit logging (all requests logged to PostgreSQL), IP whitelisting on admin routes (Docker network only), Nginx reverse proxy with security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options), request size limits (4KB), API key authentication for admin agent, webhook signature verification (WhatsApp HMAC-SHA256).
8. **Provides observability** via a health monitor service (30s polling, Redis-backed metrics), analytics scripts (token usage, resolution rates, session stats, cost tracking, top issues), a web-based admin dashboard, and health endpoints on every service.

### Operational Role

CommandDesk operates as a **production-grade AI customer support layer** that sits on top of existing helpdesk systems. It does not replace osTicket/Freshdesk/Zammad — it augments them with AI triage, auto-response, and self-service capabilities while keeping all customer data on-premises.

The system is designed to be deployed via `docker compose` with a single command, requiring only a GGUF model file and environment variables for the ticketing backends. It can also run in a standalone mode (outside Docker) using the `hermes-llama-cpp.config.yaml` and `llama-cpp-server.service` systemd unit.

The system also includes an **agent bridge** (`config/agent-bridge.yaml`) that allows the main Hermes agent to delegate helpdesk/ticket/support intents to the CommandDesk agents, making it a drop-in helpdesk capability for the broader J1 ecosystem.

---

## Why This Was Built

### Real Problem

Customer support teams face a fundamental tension: **AI helpdesk tools (Zendesk AI, Intercom Fin, Freshdesk Freddy) are powerful but expensive, send customer data to third-party cloud providers, and cannot be customized or extended by the team running them.** Open-source ticketing systems (osTicket, Zammad) are self-hosted but have no native AI capabilities. The gap between "self-hosted but dumb" and "AI-powered but cloud-locked" leaves organizations with an impossible choice: sacrifice privacy or sacrifice efficiency.

### Why Existing Tools Were Insufficient

| Tool | Limitation |
|------|-----------|
| **osTicket / Zammad** | No AI capabilities. Manual triage only. No knowledge base search. |
| **Freshdesk (free plan)** | No AI. API-only. Limited to 1 agent. |
| **Zendesk AI / Intercom Fin** | Cloud-only. Per-ticket pricing. Customer data leaves the host. No local LLM support. |
| **Generic LLM chatbots** | No ticketing integration. No multi-channel support. No workflow automation. No rate limiting or audit. |
| **DIY (LangChain + ticketing API)** | Fragile. No production hardening. No health monitoring. No session management. No human takeover flow. |

### What Triggered Development

The repository's commit history (starting 2026-06-16) shows a clear progression:

1. **Initial scaffolding** (c79c1d1) — "Initial: helpdesk agent guide, llama.cpp configs, osTicket wrapper, admin dashboard." The project started as a standalone Hermes agent with osTicket integration.
2. **Adapter pattern** (09d6ce2) — "Add ticket platform registry, adapters, and updated guide/dashboard." The plug-in architecture was introduced immediately, suggesting the author knew multi-platform support was essential from day one.
3. **Containerization** (09bd882, bdef1d3, 963133d) — CI workflow, Docker Compose, self-hosted container stacks. The system was designed for Docker-first deployment from the beginning.
4. **Multi-channel expansion** (79b140b, 8ea7a9a, 8d093ea) — WhatsApp webhook, human takeover flow, tools UI, CI pipeline, screenshots. The system became production-ready.
5. **Enterprise hardening** (dbbffa7, 68030cf) — n8n workflows, MCP registry, analytics, production compose, J1 Dev Ops dashboard. The system became an enterprise platform.
6. **Standardization** (9e7c463, de89ae1) — Documentation, ruff auto-fixes, portfolio standardization.
7. **Security audit** (5c7db2d) — "audit(CommandDesk): sanitize email references." A dedicated security pass was made.

The trigger was the realization that **no existing open-source project filled the gap between "self-hosted ticketing" and "AI-powered support"** in a way that was production-ready, secure, and extensible.

### Ecosystem Fit

CommandDesk is part of the **JorahOne (OneByJorah)** portfolio of self-hosted enterprise tools. It follows the same patterns as other J1 projects:

- **100% self-hosted** — no cloud dependencies, no telemetry, no API keys for third-party AI services.
- **Docker Compose-first deployment** — single-command startup, consistent with other J1 stacks.
- **Plug-in architecture** — the ticket platform adapter pattern (`ticket_platforms/registry.py`) mirrors the skill/plugin architecture used across J1.
- **Production hardening** — rate limiting, audit logging, health monitoring, security headers, IP whitelisting.
- **n8n workflow integration** — automation layer shared across J1 projects.
- **Hermes Agent compatibility** — the system is designed to be bridged to the main Hermes agent via the agent-bridge config, making it a drop-in helpdesk capability for the broader J1 ecosystem.
- **MCP (Model Context Protocol) support** — Freshdesk integration uses the MCP protocol, making it compatible with the broader MCP ecosystem.

The `compose/` directory contains overlay stacks for a broader self-hosted infrastructure vision:
- **Self-hosted stack**: STT (Whisper), TTS (Piper), headless browser (Alpine Chrome), Honcho (multi-agent memory)
- **Plus stack**: Alternative STT/TTS/browser/Honcho images
- **Automation**: n8n standalone
- **Monitoring**: Uptime Kuma
- **Mail**: Postal (self-hosted mail server)
- **Git**: Gitea
- **Knowledge**: SearXNG standalone
- **Storage**: PostgreSQL (pgvector) + MinIO
- **Wiki**: Outline
- **CI**: Python compile-check container

This suggests CommandDesk was envisioned as the **helpdesk component of a larger self-hosted enterprise platform**, not just a standalone tool.

---

## Operational Classification

| Category | Classification | Evidence |
|----------|---------------|----------|
| **Production** | ✅ **PRIMARY** | Production docker-compose override (`.prod.yml`) with health checks, restart policies (`always`), resource limits (CPU + memory), health monitor service (30s polling), CI pipeline (lint + build + smoke test), CodeQL scanning (Python + JavaScript + TypeScript), Dependabot (pip + npm + docker + github-actions), security audit commit in history. Designed for real customer support operations. |
| **Automation** | ✅ **PRIMARY** | n8n workflows (ticket routing with keyword classification, auto-escalation, daily digest via cron, satisfaction surveys every 4 hours, ticket-created notifications), email-to-ticket conversion (IMAP polling every 60s), WhatsApp intent detection and routing (6 intent patterns), auto-response via local LLM. |
| **Security** | ✅ **PRIMARY** | Rate limiting at 3 layers (Nginx zones: general 10r/s, API 30r/s, login 1r/s; per-session limits; WhatsApp per-minute limits), content filtering (PII patterns: password, credit_card, ssn), audit logging (all requests logged to PostgreSQL), IP whitelisting on admin routes (Docker subnet only), Nginx security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, Referrer-Policy), request size limits (4KB), API key authentication for admin agent, webhook signature verification (WhatsApp HMAC-SHA256), `.env` never committed, secrets in `.gitignore`. |
| **Observability** | ✅ **PRIMARY** | Health monitor service (30s polling, Redis-backed metrics, 7 services monitored), analytics scripts (token usage, resolution rates, session stats, cost tracking, top issues, rate limit hits), admin dashboard (web-based), health endpoints on every service, JSON-format logging, PostgreSQL audit log. |
| **Experimental** | ❌ Not applicable | The system is past experimental — it has CI, security scanning, production configs, MCP support, and is designed for real deployment. |

**Overall classification: Production / Automation / Security / Observability**

CommandDesk is a **production-grade, self-hosted AI helpdesk agent** that automates customer support workflows while maintaining full data privacy. It is the answer to "how do we get AI-powered support without sending customer data to the cloud?"

---

## Key Architectural Decisions

1. **Local LLM only** — No OpenAI/Anthropic API keys. The system uses Qwen2.5-7B via llama.cpp with 65K context. This is a deliberate privacy-first choice. The model is downloaded once via `setup.sh` and runs entirely on-premises.

2. **Adapter pattern for ticketing** — Each platform (osTicket, Freshdesk, Zammad) implements a common `Ticket` ABC with `create_ticket`, `update_ticket`, `search_tickets`, `close_ticket`. Adding a new platform means writing one class and registering it with `@register("name")`. The registry (`ticket_platforms/registry.py`) provides `get()`, `register()`, and `available()` functions.

3. **Two-agent architecture** — Separating the end-user-facing agent (no ticket creation, restricted to own tickets) from the admin agent (full access, all tickets, analytics, KB management) prevents privilege escalation through the customer-facing interface. This is enforced at the config level (`hermes-config.yaml` vs `admin-agent-config.yaml`) and at the environment level (`ALLOW_CREATE_TICKET=false` vs `true`).

4. **MCP (Model Context Protocol) support** — Freshdesk integration uses the MCP protocol (NeuraLegion/freshdesk_mcp, 41 tools), making it compatible with the broader MCP ecosystem. Other platforms use direct REST adapters. The MCP config (`mcp-config.yaml`) also defines granular permissions per agent mode (helpdesk vs admin).

5. **n8n for workflows** — Rather than building a custom workflow engine, the system delegates to n8n, which provides a visual editor, scheduling (cron), and 400+ integrations. Five pre-built workflows cover the core automation needs: ticket routing, auto-escalation, daily digest, satisfaction surveys, and ticket-created notifications.

6. **Redis for state** — Session state, rate limiting, and health metrics all live in Redis, making the agent services stateless and horizontally scalable. Redis is configured with password auth, LRU eviction (256MB max), and AOF persistence.

7. **PostgreSQL for persistence** — Tickets, users, sessions, audit logs, and cost tracking are persisted in PostgreSQL with proper indexing (10+ indexes) and foreign keys. The schema includes UUID primary keys, JSONB metadata fields, and trigger-based `updated_at` timestamps.

8. **Nginx as security gateway** — All external traffic goes through Nginx, which enforces rate limiting zones, security headers, IP whitelisting for admin routes, request size limits, and proxy caching. This keeps the application services isolated from direct external access.

9. **Docker Compose-first deployment** — The entire stack (12+ containers) is defined in a single `docker-compose.yml` with a production override (`docker-compose.prod.yml`) that adds stricter health checks, resource limits, and restart policies. A `Makefile` provides convenience commands for common operations.

10. **Agent bridge to Hermes** — The `config/agent-bridge.yaml` allows the main Hermes agent to delegate helpdesk/ticket/support intents to CommandDesk agents, making it a drop-in capability for the broader J1 ecosystem rather than a standalone tool.

---

## Repository Structure

```
CommandDesk/
├── admin/                          # Admin dashboard (static HTML)
│   └── admin-dashboard.html
├── compose/                        # Docker Compose overlay stacks
│   ├── docker-compose.yml          #   Hermes agent standalone
│   ├── docker-compose.automation.yml  # n8n standalone
│   ├── docker-compose.ci.yml       #   CI compile-check container
│   ├── docker-compose.git.yml      #   Gitea
│   ├── docker-compose.knowledge.yml  # SearXNG standalone
│   ├── docker-compose.mail.yml     #   Postal mail server
│   ├── docker-compose.monitoring.yml  # Uptime Kuma
│   ├── docker-compose.plus.yml     #   Alternative STT/TTS/browser/Honcho
│   ├── docker-compose.selfhosted.yml  # STT/TTS/browser/Honcho
│   ├── docker-compose.storage.yml  #   PostgreSQL (pgvector) + MinIO
│   ├── docker-compose.wiki.yml     #   Outline wiki
│   ├── Dockerfile                  #   Hermes agent Dockerfile
│   └── requirements.txt           #   Python deps for compose
├── config/                         # Application configuration
│   ├── admin-agent-config.yaml     #   Admin agent config (full access)
│   ├── agent-bridge.yaml           #   Hermes agent bridge config
│   ├── hermes-config.yaml          #   Helpdesk agent config (restricted)
│   ├── mcp-config.yaml             #   MCP server config + permissions
│   ├── mcp-registry.yaml           #   MCP server registry (6 platforms)
│   ├── nginx.conf                  #   Nginx reverse proxy config
│   ├── searxng-settings.yml        #   SearXNG search engine config
│   └── system-prompt.md            #   Helpdesk agent system prompt
├── scripts/                        # Utility scripts
│   ├── agent_server.py             #   FastAPI agent server (main entry point)
│   ├── analytics.py                #   Analytics report generator
│   ├── email_fetcher.py            #   IMAP email-to-ticket service
│   ├── health_monitor.py           #   Service health monitoring (30s loop)
│   ├── index_kb.py                 #   Knowledge base ChromaDB indexer
│   ├── init-db.sql                 #   PostgreSQL schema (7 tables, 15+ indexes)
│   ├── rate_limiter.py             #   Rate limiter middleware
│   ├── session_manager.py          #   Redis + PostgreSQL session manager
│   ├── setup.sh                    #   One-time setup script
│   └── whatsapp_webhook.py         #   WhatsApp webhook receiver (639 lines)
├── skills/                         # AI agent skills
│   ├── manifest.yaml               #   Skill manifest (j1-helpdesk + persona)
│   └── persona-customer-support/   #   External skill (hazelugo/fav_gits)
│       ├── SKILL.md
│       └── .skillfish.json
├── ticket_platforms/               # Ticketing adapter library
│   ├── __init__.py                 #   Package exports
│   ├── base.py                     #   Ticket ABC (4 abstract methods)
│   ├── email.py                    #   Email-to-ticket adapter
│   ├── freshdesk.py                #   Freshdesk REST API v2 adapter
│   ├── osticket.py                 #   osTicket REST API v1 adapter
│   ├── registry.py                 #   Adapter registry (register/get/available)
│   └── zammad.py                   #   Zammad REST API adapter
├── tools-ui/                       # Web UI components
│   ├── dashboard.html              #   Admin dashboard
│   ├── index.html                  #   Chat widget
│   ├── mobile-app.html             #   Mobile PWA
│   ├── Dockerfile                  #   Nginx-based UI container
│   └── manifest.json               #   PWA manifest
├── workflows/                      # n8n workflow definitions
│   ├── auto-escalation.json        #   Escalation to admin + Slack
│   ├── daily-digest.json           #   Weekday 9AM stats digest
│   ├── satisfaction-survey.json    #   Every 4h survey for closed tickets
│   ├── ticket-created.json         #   New ticket notification
│   └── ticket-routing.json         #   Keyword-based ticket classification
├── .github/                        # GitHub configuration
│   ├── dependabot.yml              #   pip + npm + docker + github-actions
│   ├── ISSUE_TEMPLATE/             #   Bug report + feature request
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── ci.yml                  #   Lint + config check + build + smoke test
│       └── codeql.yml              #   CodeQL security analysis (Python/JS/TS)
├── docker-compose.yml              # Main deployment (12 services)
├── docker-compose.prod.yml         # Production override (health checks, limits)
├── docker-compose.dev.yml          # Development override (debug, exposed ports)
├── Dockerfile                      # Backend agent container
├── Dockerfile.email                # Email fetcher container
├── Dockerfile.whatsapp             # WhatsApp webhook container
├── Makefile                        # Build automation (20+ targets)
├── requirements.txt                # Python dependencies (14 packages)
├── .env.example                    # Environment template (30+ vars)
├── .gitignore                      # 20 patterns
├── README.md                       # Project documentation
├── LICENSE                         # MIT
├── CODE_OF_CONDUCT.md              # Contributor Covenant v2.1
├── CONTRIBUTING.md                 # Contribution guidelines
├── SECURITY.md                     # Security policy (90-day disclosure)
├── hermes-llama-cpp.config.yaml    # Standalone Hermes config (non-Docker)
├── llama-cpp-server.service       # systemd unit for llama.cpp
├── memory_setup.py                 # SQLite memory setup (standalone mode)
├── osticket_tool.py                # Standalone osTicket tool (pre-adapter)
├── helpdesk-agent-diagram-guide.html  # Architecture diagram
├── dashboard-mockup.png            # Dashboard screenshot
└── dashboard-realistic.png         # Dashboard screenshot
```

### Notable Observations

- **`knowledge-base/` directory does not exist** — Referenced in `docker-compose.yml` as a volume mount but absent from the repo. The `setup.sh` script creates a sample `welcome.md` file, but the directory itself is not tracked.
- **`certs/` directory is gitignored** — Referenced in `docker-compose.yml` and `nginx.conf` for HTTPS, but self-signed certs are generated by `setup.sh`.
- **`models/` directory is gitignored** — Expected; GGUF model files are large and downloaded by `setup.sh`.
- **No `tests/` directory** — No test files exist anywhere in the repo. The CI pipeline has a smoke test (PostgreSQL + Redis connectivity) but no unit tests or integration tests.
- **Dependabot configured for `npm` but no `package.json`** — The `dependabot.yml` lists `npm` as an ecosystem, but there is no `package.json` in the repo. This is a template vestige.
- **Two compose layers** — The root `docker-compose.yml` is the full production stack (12 services). The `compose/docker-compose.yml` is a simpler standalone Hermes agent. The `compose/` directory also contains 10 overlay stacks for a broader self-hosted infrastructure vision.
- **Two osTicket implementations** — `osticket_tool.py` (standalone, pre-adapter) and `ticket_platforms/osticket.py` (adapter-based). The standalone version appears to be the original approach, superseded by the adapter pattern.
- **Standalone mode** — `hermes-llama-cpp.config.yaml`, `llama-cpp-server.service`, and `memory_setup.py` suggest the system was originally designed to run outside Docker as a standalone Hermes agent with SQLite memory.

---

## Notes

- **Security audit in history**: Commit `5c7db2d` ("audit(CommandDesk): sanitize email references") and `68216b0` ("security: redact exposed tailscale IPs and demo emails") show active security maintenance. This is a positive maturity signal.
- **Very recent project**: All commits are from June-July 2026. The project is under active development.
- **Dependabot ecosystem mismatch**: Dependabot is configured for `npm` ecosystem, but no `package.json` exists. This is a template vestige from the J1 repo template.
- **No test files**: The repo has no `tests/` directory and no test files. The CI pipeline has a basic smoke test but no unit/integration tests. This is a gap for a production-classified repo.
- **Knowledge base directory missing**: `knowledge-base/` is referenced in compose but doesn't exist in the repo. The `setup.sh` creates a sample file, but the directory itself is not tracked.
- **Two osTicket implementations coexist**: `osticket_tool.py` (standalone) and `ticket_platforms/osticket.py` (adapter). The standalone version may be dead code.
- **Broad self-hosted vision**: The `compose/` directory contains 10 overlay stacks (STT, TTS, browser, Honcho, Gitea, Postal, Outline, MinIO, Uptime Kuma, SearXNG) that go well beyond helpdesk functionality. This suggests CommandDesk was envisioned as the **helpdesk component of a larger self-hosted enterprise platform**.
