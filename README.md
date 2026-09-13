<div align="center">

![CommandDesk banner](docs/assets/banner.svg)

# CommandDesk

**A self-hosted AI helpdesk agent** — multi-platform ticketing, email-to-ticket, knowledge-base answers, and live cost tracking, running on local LLMs.

<a href="https://github.com/OneByJorah/CommandDesk/stargazers"><img src="https://img.shields.io/github/stars/OneByJorah/CommandDesk?style=flat-square" alt="Stars"></a>
<a href="https://github.com/OneByJorah/CommandDesk/commits"><img src="https://img.shields.io/github/last-commit/OneByJorah/CommandDesk?style=flat-square" alt="Last commit"></a>
<a href="LICENSE"><img src="https://img.shields.io/github/license/OneByJorah/CommandDesk?style=flat-square" alt="License"></a>
<img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/fastapi-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
<img src="https://img.shields.io/badge/llm-llama.cpp-FF6F00?style=flat-square" alt="llama.cpp">

</div>

![CommandDesk screenshot](docs/assets/screenshot.png)

## What This Is

Helpdesk AI is usually a paid SaaS add-on, and your ticket data leaves the building. CommandDesk runs the whole pipeline locally: it ingests email and chat into a unified queue, answers from your own knowledge base with a local LLM, and tracks the AI cost of every ticket. Humans can take over at any point, and n8n workflows handle routing, escalation, and surveys.

## Quick Start

```bash
git clone https://github.com/OneByJorah/CommandDesk.git
cd CommandDesk
cp .env.example .env        # configure AI + email settings
docker compose up -d
```

| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost/dashboard/ (nginx reverse proxy) |
| **Widget preview** | http://localhost:8484 |
| **Agent API** | http://localhost:8080 |
| **WhatsApp webhook** | http://localhost:9090 |

### Local development

```bash
pip install -r requirements.txt
uvicorn scripts.agent_server:app --reload --port 8080
```

## Features

- **Multi-platform queue** — email, web widget, WhatsApp, osTicket, Freshdesk, and Zammad in one place.
- **AI responses** — local llama.cpp or OpenAI GPT, with context-aware replies.
- **Knowledge base** — ChromaDB vector search over your documentation.
- **Email-to-ticket** — IMAP ingestion creates tickets automatically.
- **SLA management** — define SLAs with automatic escalation on breach.
- **Cost tracking** — per-ticket, per-agent, and per-session AI usage costs in real time.
- **Rate limiting** — per-session limits with automatic blocking and audit logging.
- **Workflow automation** — n8n handles routing, escalation, satisfaction surveys, and daily digests.
- **Admin dashboard** — live queue, performance metrics, audit logs, and service health.

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

## API Endpoints

**Helpdesk agent** (port 8080):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Agent health check |
| `/chat` | POST | Send a user message, get an AI response |
| `/session/{session_id}` | GET | Session usage info |

**WhatsApp webhook** (port 9090):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook/whatsapp` | GET | Webhook verification challenge |
| `/webhook/whatsapp` | POST | Receive WhatsApp messages |
| `/admin/takeover/{phone}` | POST | Human takes over a conversation |
| `/admin/resume/{phone}` | POST | Re-enable the bot |
| `/admin/queue` | GET | View the human support queue |

## Ticket Statuses

| Status | Description |
|--------|-------------|
| `open` | New ticket awaiting response |
| `in_progress` | Being handled by an agent |
| `waiting` | Awaiting customer response |
| `resolved` | Issue resolved |
| `closed` | Ticket archived |

## Configuration

Core variables (see [.env.example](.env.example) for the full list):

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_API_BASE` | `http://llama:8081/v1` | LLM OpenAI-compatible endpoint |
| `LLM_MODEL` | `qwen2.5-7b-instruct` | Model name sent to the LLM |
| `LLAMA_MODEL_PATH` | `/models/qwen2.5-7b-instruct-q4_k_m.gguf` | Local GGUF model path |
| `REDIS_URL` | `redis://redis:6379/0` | Redis for sessions & rate limiting |
| `POSTGRES_URL` | `postgresql://helpdesk:helpdesk@postgres:5432/helpdesk` | PostgreSQL persistence |
| `CHROMA_URL` | `http://chroma:8000` | ChromaDB vector store |
| `SEARX_URL` | `http://searxng:8080` | SearXNG metasearch |
| `RATE_LIMIT_PER_SESSION` | `50` | Max messages per session window |
| `RATE_LIMIT_WINDOW` | `3600` | Rate-limit window (seconds) |
| `MAX_MESSAGE_LENGTH` | `4000` | Max message characters |
| `IMAP_HOST` / `IMAP_USER` / `IMAP_PASSWORD` | — | Email-to-ticket ingestion |
| `TICKET_PLATFORM` | `osticket` | Default ticket backend |
| `OSTICKET_URL` / `OSTICKET_API_KEY` | — | osTicket API |
| `FRESHDESK_URL` / `FRESHDESK_API_KEY` | — | Freshdesk API |
| `WHATSAPP_TOKEN` / `WHATSAPP_PHONE_NUMBER_ID` | — | WhatsApp Business API |

> [!WARNING]
> `HERMES_API_KEY`, `ADMIN_API_KEY`, `DB_PASSWORD`, and the platform API keys are secrets. Keep them in `.env` (never committed).

## Compose Overlays

The base `docker-compose.yml` brings up the core stack; add overlays for extra services in `compose/`:

| Overlay | Adds |
|---------|------|
| `docker-compose.mail.yml` | Mail handling |
| `docker-compose.knowledge.yml` | Knowledge-base indexing |
| `docker-compose.monitoring.yml` | Monitoring |
| `docker-compose.automation.yml` | n8n automation |
| `docker-compose.selfhosted.yml` | Self-hosted extras |
| `docker-compose.storage.yml` | Object/file storage |
| `docker-compose.wiki.yml` / `.git.yml` / `.ci.yml` / `.plus.yml` | Wiki, git, CI, extras |

## Web UI

| File | Purpose |
|------|---------|
| `index.html` | Landing page with features, architecture, and quick start |
| `admin/admin-dashboard.html` | Real-time admin dashboard: metrics, queue, service health, costs, audit log |
| `tools-ui/index.html` | Embeddable WhatsApp-style widget preview with a configuration panel |

## Project Structure

```
CommandDesk/
├── admin/admin-dashboard.html  # Real-time ops dashboard
├── compose/                    # Docker Compose overlays
├── config/                     # Agent & service configuration
├── scripts/                    # Backend agents & utilities
│   ├── agent_server.py         # Core helpdesk agent (FastAPI)
│   ├── email_fetcher.py        # Email ingestion (IMAP)
│   ├── session_manager.py      # Session lifecycle
│   ├── rate_limiter.py         # Rate limiting engine
│   ├── health_monitor.py       # Service health checks
│   ├── analytics.py            # Cost & usage analytics
│   └── whatsapp_webhook.py     # WhatsApp integration
├── skills/                     # AI skill definitions
├── ticket_platforms/           # osTicket, Freshdesk, Zammad, email adapters
├── tools-ui/                   # Embeddable web widget
├── workflows/                  # n8n workflow JSONs
├── docker-compose.yml          # Production deployment
├── Dockerfile                  # Helpdesk agent image
└── .env.example
```

## Use Cases

1. **Small-team helpdesk** — automate first-line responses without a SaaS bill.
2. **Privacy-sensitive support** — keep tickets and customer data on-premises.
3. **AI cost visibility** — track exactly what each automated ticket costs in tokens.

## Tech Stack

Python 3.10+ · FastAPI · llama.cpp / OpenAI · ChromaDB · PostgreSQL · Redis · SearXNG · n8n · Docker Compose · HTML/CSS

## Screenshots

| View | |
|---|---|
| ![admin dashboard](docs/screenshots/admin-dashboard.png) | ![ai assistant](docs/screenshots/ai-assistant.png) |
| ![costs](docs/screenshots/costs.png) | ![widget preview](docs/screenshots/widget-preview.png) |
| ![landing](docs/screenshots/landing.png) | ![mobile](docs/screenshots/main.mobile.png) |

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). [Open an issue](https://github.com/OneByJorah/CommandDesk/issues).

## License

MIT — see [LICENSE](LICENSE).

## Connect

- [jorahone.com](https://jorahone.com)
- [GitHub Org](https://github.com/OneByJorah)
- [info@jorahone.com](mailto:info@jorahone.com)
