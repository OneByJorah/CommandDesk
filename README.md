<div align="center">

# CommandDesk

**Self-hosted AI-powered helpdesk agent** — local LLMs, multi-platform ticketing, workflow automation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688?logo=fastapi)]()
[![llama.cpp](https://img.shields.io/badge/LLM-llama.cpp-FF6F00)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub stars](https://img.shields.io/github/stars/OneByJorah/CommandDesk?style=social)](https://github.com/OneByJorah/CommandDesk)

<br>

<a href="https://github.com/OneByJorah/CommandDesk">
  <img src="docs/screenshots/admin-dashboard.png" alt="CommandDesk admin dashboard" width="95%">
</a>

<br>

[🚀 Live Demo](https://github.com/OneByJorah/CommandDesk) &nbsp;·&nbsp; [📘 Docs](docs/) &nbsp;·&nbsp; [🐛 Report Bug](https://github.com/OneByJorah/CommandDesk/issues) &nbsp;·&nbsp; [✨ Feature Request](https://github.com/OneByJorah/CommandDesk/issues)

</div>

---

## Features

| Category | Capabilities |
|----------|-------------|
| **Multi-Platform** | Email, Web Widget, WhatsApp, osTicket, Freshdesk, Zammad — unified queue |
| **AI Responses** | Local LLM (llama.cpp) or OpenAI GPT — intelligent, context-aware replies |
| **Knowledge Base** | ChromaDB vector search — instant retrieval from your documentation |
| **SLA Management** | Define SLAs, automatic escalation when breached |
| **Cost Tracking** | Per-ticket, per-agent, per-session AI usage costs — real-time |
| **Rate Limiting** | Per-session limits with automatic blocking and audit logging |
| **Workflow Automation** | n8n-powered: routing, escalation, satisfaction surveys, daily digests |
| **Agent Dashboard** | Real-time queue, performance metrics, audit logs, service health |

## Architecture

```
                  ┌──────────────────────────────────────────────────┐
                  │                     User                         │
                  │  (WhatsApp / Web Widget / Email / API / Portal)  │
                  └──────────────────────┬───────────────────────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    │            Helpdesk Agent                │
                    │     (agent_server.py · FastAPI)          │
                    │  Session Mgmt · Rate Limiting · Routing  │
                    └──────┬──────────┬──────────┬─────────────┘
                           │          │          │
              ┌────────────┴─┐  ┌─────┴─────┐  └──────────────┐
              │   LLM Core   │  │  Context   │   Ticket Platforms│
              │ llama.cpp /  │  │ ChromaDB ·│   osTicket · FD  │
              │ OpenAI API   │  │ SearXNG   │   Zammad · Email │
              └──────────────┘  └───────────┘   └────────────────┘
                                                    │
              ┌──────────────────────────┐   ┌──────┴──────┐
              │    Admin Dashboard       │   │ n8n Workflows│
              │ PostgreSQL · Redis · Logs│   │ Escalation   │
              │ Costs · Metrics · Audit  │   │ Surveys      │
              └──────────────────────────┘   └─────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.10+ |
| **API Framework** | FastAPI (async) |
| **LLM** | llama.cpp (local) / OpenAI GPT |
| **Vector DB** | ChromaDB |
| **Database** | PostgreSQL + Redis |
| **Search** | SearXNG (private metasearch) |
| **Automation** | n8n |
| **Container** | Docker Compose |
| **Frontend** | HTML/CSS dashboard + embeddable widget |

## Project Structure

```
CommandDesk/
├── admin/                    # Admin dashboard UI
│   └── admin-dashboard.html  # Real-time ops dashboard
├── compose/                  # Docker Compose overlays
│   ├── docker-compose.mail.yml
│   ├── docker-compose.knowledge.yml
│   ├── docker-compose.monitoring.yml
│   └── ...
├── config/                   # Agent & service configuration
│   ├── agent-bridge.yaml
│   ├── admin-agent-config.yaml
│   ├── mcp-config.yaml
│   ├── system-prompt.md
│   └── ...
├── docs/                     # Documentation & screenshots
│   └── assets/
├── scripts/                  # Backend agents & utilities
│   ├── agent_server.py       # Core helpdesk agent (FastAPI)
│   ├── email_fetcher.py      # Email ingestion (IMAP)
│   ├── session_manager.py    # Session lifecycle
│   ├── rate_limiter.py       # Rate limiting engine
│   ├── health_monitor.py     # Service health checks
│   ├── analytics.py          # Cost & usage analytics
│   ├── whatsapp_webhook.py   # WhatsApp integration
│   └── ...
├── skills/                   # AI skill definitions
│   └── persona-customer-support/
├── ticket_platforms/         # Platform integrations
│   ├── base.py               # Abstract base
│   ├── osticket.py            # osTicket API
│   ├── freshdesk.py          # Freshdesk API
│   ├── zammad.py             # Zammad API
│   └── email.py              # Email platform
├── tools-ui/                 # Embeddable web widget
│   ├── index.html            # Widget preview
│   ├── dashboard.html
│   └── mobile-app.html
├── workflows/                # n8n workflow JSONs
│   ├── ticket-routing.json
│   ├── auto-escalation.json
│   ├── satisfaction-survey.json
│   └── ...
├── docker-compose.yml        # Production deployment
├── Dockerfile                # Helpdesk agent image
├── Makefile                  # Common commands
├── hermes-llama-cpp.config.yaml
├── osticket_tool.py
└── memory_setup.py
```

## Quick Start

```bash
git clone https://github.com/OneByJorah/CommandDesk.git
cd CommandDesk

cp .env.example .env          # Configure AI & email settings
docker compose up -d          # One-command launch
```

| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost/dashboard/ (nginx reverse proxy) |
| **Widget Preview** | http://localhost:8484 |
| **Agent API** | http://localhost:8080 |
| **WhatsApp Webhook** | http://localhost:9090 |

### Local Development

```bash
# Backend
pip install -r requirements.txt
uvicorn scripts.agent_server:app --reload --port 8080

# Web tools
cd tools-ui && python3 -m http.server 3000
```

## Environment Variables

Core variables (see [.env.example](.env.example) for the full list):

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_API_BASE` | `http://llama:8081/v1` | LLM OpenAI-compatible endpoint |
| `LLM_MODEL` | `qwen2.5-7b-instruct` | Model name sent to the LLM |
| `REDIS_URL` | `redis://redis:6379/0` | Redis for sessions & rate limiting |
| `POSTGRES_URL` | `postgresql://helpdesk:helpdesk@postgres:5432/helpdesk` | PostgreSQL persistence |
| `CHROMA_URL` | `http://chroma:8000` | ChromaDB vector store |
| `SEARX_URL` | `http://searxng:8080` | SearXNG metasearch |
| `RATE_LIMIT_PER_SESSION` | `50` | Max messages per session window |
| `MAX_MESSAGE_LENGTH` | `4000` | Max message chars |
| `IMAP_HOST` / `IMAP_USER` / `IMAP_PASSWORD` | — | Email-to-ticket ingestion |
| `WHATSAPP_TOKEN` / `WHATSAPP_PHONE_NUMBER_ID` | — | WhatsApp Business API |

## API Endpoints

**Helpdesk Agent** (port 8080):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Agent health check |
| `/chat` | POST | Send user message, get AI response |
| `/session/{session_id}` | GET | Session usage info |

**WhatsApp Webhook** (port 9090):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook/whatsapp` | GET | Webhook verification challenge |
| `/webhook/whatsapp` | POST | Receive WhatsApp messages |
| `/admin/takeover/{phone}` | POST | Human takes over a conversation |
| `/admin/resume/{phone}` | POST | Re-enable the bot |
| `/admin/queue` | GET | View human support queue |

## Ticket Statuses

| Status | Description |
|--------|-------------|
| `open` | New ticket awaiting response |
| `in_progress` | Being handled by an agent |
| `waiting` | Awaiting customer response |
| `resolved` | Issue resolved |
| `closed` | Ticket archived |

## Web UI

The project ships with two web interfaces:

- **`index.html`** — Landing page with features, architecture, and quick-start (dark theme)
- **`admin/admin-dashboard.html`** — Full admin dashboard with real-time metrics, ticket queue, service health, cost analytics, and audit log (dark theme)
- **`tools-ui/index.html`** — Embeddable WhatsApp-style widget preview with configuration panel

Open the landing page locally:

```bash
python3 -m http.server 8102
# → http://localhost:8102
```

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Security

Report vulnerabilities to **info@jorahone.com** or see [SECURITY.md](SECURITY.md).

## License

MIT © [Jhonattan L. Jimenez](https://github.com/OneByJorah)

---

<p align="center">Built with 🌴 by <a href="https://github.com/OneByJorah">OneByJorah</a> · <a href="https://jorahone.com">jorahone.com</a></p>
