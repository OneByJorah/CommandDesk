<div align="center">

# CommandDesk

**Self-hosted AI-powered helpdesk agent** — local LLMs, multi-platform ticketing, workflow automation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)]()
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688?logo=fastapi)]()
[![llama.cpp](https://img.shields.io/badge/LLM-llama.cpp-FF6F00)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub stars](https://img.shields.io/github/stars/OneByJorah/CommandDesk?style=social)](https://github.com/OneByJorah/CommandDesk)

<br>

<a href="https://github.com/OneByJorah/CommandDesk">
  <img src="docs/assets/screenshot.png" alt="CommandDesk preview" width="95%">
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
| **Dashboard** | http://localhost:8000 |
| **Admin UI** | http://localhost:8000/admin |
| **Widget Preview** | http://localhost:8000/widget |
| **Agent API** | http://localhost:8080 |

### Local Development

```bash
# Backend
pip install -r requirements.txt
uvicorn scripts.agent_server:app --reload --port 8080

# Web tools
cd tools-ui && python3 -m http.server 3000
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Backend API port |
| `DATABASE_URL` | `sqlite:///commanddesk.db` | Database connection string |
| `OPENAI_API_KEY` | — | OpenAI API key (optional, use local LLM) |
| `LLAMA_CPP_URL` | `http://llama-cpp:8080` | Local LLM endpoint |
| `SMTP_HOST` | — | Email server for ticket ingestion |
| `SMTP_PORT` | `587` | Email server port |
| `CHROMA_DB_PATH` | `./chroma_db` | Vector database path |
| `RATE_LIMIT_MAX` | `50` | Max messages per session |
| `COST_PER_1K_TOKENS` | `0.02` | Cost per 1K tokens for tracking |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tickets` | GET/POST | Manage tickets |
| `/api/tickets/{id}` | GET/PUT | Get/update ticket |
| `/api/tickets/{id}/respond` | POST | AI auto-response |
| `/api/sessions` | GET | List active sessions |
| `/api/agents` | GET | List helpdesk agents |
| `/api/knowledge/search` | POST | Search knowledge base |
| `/api/analytics/costs` | GET | Cost analytics |
| `/api/analytics/performance` | GET | Agent performance |
| `/api/health` | GET | System health check |

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
