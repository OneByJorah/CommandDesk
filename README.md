# CommandDesk

**Self-hosted AI helpdesk with multi-platform ticketing, WhatsApp chat, email-to-ticket, knowledge base, Freshdesk MCP, and a plug-in agent architecture.**

[![CI](https://github.com/JorahOne-Services/CommandDesk/actions/workflows/ci.yml/badge.svg)](https://github.com/JorahOne-Services/CommandDesk/actions/workflows/ci.yml)
[![Security Scan](https://github.com/JorahOne-Services/CommandDesk/actions/workflows/security-scan.yml/badge.svg)](https://github.com/JorahOne-Services/CommandDesk/actions/workflows/security-scan.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-311/)

100% local and free. Compatible with Hermes Agent and the broader agent-skills ecosystem.

![Admin Dashboard](https://v3b.fal.media/files/b/0a9f159d/EQkpV4ZcXRrZthURYu5rA_Pz09bZEi.png)

## Features

- 🤖 **AI Helpdesk Agent** — Answers customer questions, searches tickets, updates status
- 📱 **WhatsApp Integration** — Customers chat with your bot on WhatsApp
- 🔌 **Plug-in Architecture** — Main Hermes can delegate to helpdesk agent or admin agent
- 📧 **Email-to-Ticket** — IMAP polling creates tickets automatically
- 🎫 **Multi-Platform** — osTicket, Freshdesk (free plan via MCP), Zammad adapters
- 📚 **Knowledge Base** — ChromaDB-powered semantic search
- 🔍 **Web Search** — Self-hosted SearXNG
- 🔧 **Freshdesk MCP** — 41 tools via Model Context Protocol
- 👤 **Human Takeover** — Customers can request human support; you take over the conversation
- 📊 **Admin Dashboard** — Cost tracking, session monitoring, audit log
- 🛡️ **Security** — Rate limiting, session limits, content filtering, audit logging
- 🔄 **Workflow Automation** — n8n for escalation, notifications

## Architecture

![Architecture](https://v3b.fal.media/files/b/0a9f15a1/K4zIkK7RgiNafiVPq1e7l_posoPUOk.png)

```
                    ┌─────────────────┐
                    │  Your Main Hermes│
                    │  (personal chat) │
                    └────────┬────────┘
                             │ delegates to
              ┌──────────────┼──────────────┐
              ▼              │              ▼
    ┌─────────────────┐      │    ┌─────────────────┐
    │  Helpdesk Agent  │      │    │  Admin Agent     │
    │  (port 8080)     │      │    │  (port 8082)     │
    │  - search tickets│      │    │  - all tickets   │
    │  - update own    │      │    │  - cost analytics│
    │  - KB search     │      │    │  - system health │
    │  - web search    │      │    │  - KB management │
    └────────┬────────┘      │    └────────┬────────┘
             │               │             │
    ┌────────┴───────────────┴─────────────┴────────┐
    │              Internal Services                  │
    ├────────────────────────────────────────────────┤
    │  llama.cpp (8081)  │  ChromaDB (8000)          │
    │  SearXNG (8888)    │  PostgreSQL (5432)        │
    │  Redis (6379)      │  n8n (5678)               │
    │  Nginx (80/443)    │  WhatsApp Webhook (9090)  │
    │  Health Monitor    │  Tools UI (8484)          │
    └────────────────────────────────────────────────┘
```

## WhatsApp Chat

![WhatsApp Chat](https://v3b.fal.media/files/b/0a9f159f/nPYhqAeYe-YSlZYmuChyA_beG9ouMO.png)

Customers can message your WhatsApp number and the AI agent will:

1. **Greet** them with a welcome message and menu
2. **Search tickets** — asks for email, shows their existing tickets
3. **Create tickets** — collects details, creates via osTicket/Freshdesk
4. **Human takeover** — queues them and notifies you to take over

When a customer requests a human:
- 🔔 You get a WhatsApp notification
- 🤖 Bot pauses for that customer
- 👤 You take over the conversation manually
- 🔄 Resume bot anytime via admin endpoint

## Security Model

| Layer | Protection |
|-------|-----------|
| **Rate Limiting** | 50 requests/session/hour (configurable) |
| **Session Duration** | 2-hour max per session |
| **Message Length** | 4000 chars max |
| **Content Filter** | Blocks password/credit_card/SSN in responses |
| **Audit Log** | All requests logged to PostgreSQL |
| **Network** | Internal services bound to 127.0.0.1 |
| **Admin Agent** | IP-whitelisted (Docker network only) |
| **Nginx** | Security headers, request size limits, rate zones |
| **WhatsApp** | HMAC signature verification |

**End users CANNOT create tickets via the AI agent.** Tickets are created via:
- Email (IMAP polling)
- osTicket web portal
- Freshdesk web portal
- WhatsApp (collected details → adapter)

## Getting Started

**Prerequisites:** Docker Engine 24+ and Docker Compose v2+ must be installed and running.

```bash
# 1. Verify Docker is active (required)
docker info >/dev/null 2>&1 || echo "Docker daemon is not running"
docker compose version

# 2. Clone the repository
git clone https://github.com/OneByJorah/CommandDesk.git
cd CommandDesk

# 3. Run setup
./scripts/setup.sh

# 4. Configure
cp .env.example .env
# Edit .env with your IMAP credentials and ticket platform settings

# 5. Start
docker compose up -d

# 6. Index knowledge base
docker compose exec helpdesk-agent python3 scripts/index_kb.py

# 7. Open
# Dashboard: http://localhost/dashboard/
# Helpdesk API: http://localhost/helpdesk/health
# Admin API: http://localhost/admin/health
# n8n: http://localhost:5678
# Widget UI: http://localhost:8484
```

## Configuration

### Environment Variables

See `.env.example` for all variables. Key ones:

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_PER_SESSION` | 50 | Max requests per session |
| `MAX_SESSION_DURATION` | 7200 | Max session duration (seconds) |
| `IMAP_HOST` | — | IMAP server for email-to-ticket |
| `OSTICKET_API_KEY` | — | osTicket API key |
| `FRESHDESK_API_KEY` | — | Freshdesk API key |
| `FRESHDESK_DOMAIN` | — | Freshdesk subdomain |
| `WHATSAPP_TOKEN` | — | WhatsApp Business API token |
| `WHATSAPP_PHONE_NUMBER_ID` | — | WhatsApp phone number ID |
| `ADMIN_PHONE_NUMBER` | — | Your WhatsApp for takeover notifications |
| `LLM_MODEL` | qwen2.5-7b-instruct | LLM model name |

### WhatsApp Setup

1. Set up WhatsApp Business API (via Meta or a provider like 360dialog)
2. Configure webhook URL: `https://your-server.com/webhook/whatsapp`
3. Set `WHATSAPP_TOKEN` and `WHATSAPP_PHONE_NUMBER_ID` in `.env`
4. Set `ADMIN_PHONE_NUMBER` to your personal WhatsApp
5. Start: `docker compose up -d whatsapp-webhook`

### Freshdesk MCP

The Freshdesk MCP server (NeuraLegion/freshdesk_mcp) provides 41 tools:

- **Tickets**: list, view, create, search, update
- **Conversations**: list, reply, add notes
- **Contacts**: list, view, create, update, search
- **Companies**: list, view, create, update, search
- **Agents**: list, view, groups
- **KB**: categories, folders, articles, search
- **Time tracking**: list, create, toggle timer
- **Canned responses**: folders, list, view

Configure in `config/mcp-config.yaml` with your Freshdesk domain and API key.

### Plug-in with Main Hermes

To connect this helpdesk agent to your main Hermes Agent:

```yaml
# In your main Hermes config
bridges:
  helpdesk-agent:
    url: "http://helpdesk-agent:8080"
    triggers: ["ticket", "helpdesk", "support", "my issue"]
  admin-agent:
    url: "http://admin-agent:8082"
    triggers: ["admin", "manage tickets", "cost analytics"]
```

## Ticket Platforms

| Platform | Status | Method |
|----------|--------|--------|
| osTicket | ✅ Full | REST API adapter |
| Freshdesk (free) | ✅ Full | MCP server (41 tools) |
| Zammad | ✅ Full | REST API adapter |
| Email (IMAP) | ✅ Full | IMAP polling → adapter |

## API Endpoints

### Helpdesk Agent (port 8080)

```
POST /chat          — Send a message (session_id optional for new sessions)
GET  /health        — Health check
GET  /session/{id}  — Session info
```

### Admin Agent (port 8082)

```
POST /chat          — Full access to all tools
GET  /health        — Health check
GET  /tickets       — List all tickets (paginated)
GET  /costs         — Cost analytics
GET  /system        — System health
```

### WhatsApp Webhook (port 9090)

```
GET  /webhook/whatsapp  — Webhook verification
POST /webhook/whatsapp  — Receive WhatsApp messages
POST /admin/takeover/{phone}  — Take over conversation
POST /admin/resume/{phone}    — Re-enable bot
GET  /admin/queue             — View human support queue
```

## Adding Knowledge Base Articles

1. Place `.md` or `.txt` files in `knowledge-base/`
2. Run: `docker compose exec helpdesk-agent python3 scripts/index_kb.py`
3. Agent will automatically find and cite them

## Monitoring

- **Admin Dashboard**: `http://localhost/dashboard/`
- **Tools UI / Widget Config**: `http://localhost:8484`
- **n8n Workflows**: `http://localhost:5678`
- **Health Monitor**: Metrics stored in Redis every 30s
- **Logs**: `docker compose logs -f helpdesk-agent`

## Makefile Commands

```bash
make start          # Start all services
make stop           # Stop all services
make logs           # View all logs
make health         # Check service health
make index-kb       # Index knowledge base
make dev            # Start in development mode
make shell          # Open shell in agent container
make psql           # Open PostgreSQL shell
make test-api       # Test agent API
```

## Resource Requirements

| Service | RAM Limit | CPU |
|---------|-----------|-----|
| llama.cpp (7B Q4) | 7GB | 6 cores |
| Helpdesk Agent | 2GB | 2 cores |
| Admin Agent | 2GB | 2 cores |
| ChromaDB | 2GB | 2 cores |
| PostgreSQL | 1GB | 1 core |
| Redis | 300MB | 1 core |
| WhatsApp Webhook | 500MB | 1 core |
| Others | ~2GB | shared |
| **Total** | **~16GB** | **6 cores** |

## File Structure

```
CommandDesk/
├── docker-compose.yml          # Full stack definition
├── Dockerfile                  # Main agent container
├── Dockerfile.email            # Email fetcher container
├── Dockerfile.whatsapp         # WhatsApp webhook container
├── Makefile                    # Common commands
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── SECURITY.md                 # Security policy
├── CONTRIBUTING.md             # Contribution guide
├── setup.cfg                   # Test configuration
├── .github/
│   ├── dependabot.yml          # Dependency updates
│   └── workflows/
│       ├── ci.yml              # CI pipeline
│       └── security-scan.yml   # Security scanning
├── docs/
│   ├── runbook.md              # Operations runbook
│   ├── api.md                  # API documentation
│   └── configuration.md        # Configuration guide
├── tests/
│   ├── test_rate_limiter.py    # Rate limiter tests
│   ├── test_email_fetcher.py   # Email fetcher tests
│   ├── test_analytics.py       # Analytics tests
│   ├── test_index_kb.py        # KB indexer tests
│   └── test_health_monitor.py  # Health monitor tests
├── config/
│   ├── hermes-config.yaml      # Helpdesk agent config
│   ├── admin-agent-config.yaml # Admin agent config
│   ├── agent-bridge.yaml       # Delegation rules
│   ├── mcp-config.yaml         # Freshdesk MCP config
│   ├── nginx.conf              # Reverse proxy
│   ├── searxng-settings.yml    # Search config
│   └── system-prompt.md       # Agent persona
├── ticket_platforms/
│   ├── base.py                 # Abstract adapter
│   ├── registry.py             # Platform registry
│   ├── email.py                # Email-to-ticket
│   ├── osticket.py             # osTicket adapter
│   ├── freshdesk.py            # Freshdesk REST adapter
│   └── zammad.py               # Zammad adapter
├── scripts/
│   ├── agent_server.py         # FastAPI agent server
│   ├── whatsapp_webhook.py     # WhatsApp integration
│   ├── rate_limiter.py         # Rate limiting
│   ├── session_manager.py      # Session management
│   ├── health_monitor.py       # Health checks
│   ├── email_fetcher.py        # IMAP polling
│   ├── index_kb.py             # Knowledge base indexer
│   ├── init-db.sql             # Database schema
│   ├── analytics.py            # Analytics reports
│   └── setup.sh                # Setup script
├── admin/
│   └── admin-dashboard.html    # Monitoring dashboard
├── tools-ui/
│   ├── index.html              # Widget config UI
│   └── Dockerfile              # Nginx container
├── knowledge-base/             # Place .md/.txt files here
└── workflows/                  # n8n workflow JSONs
```

## Documentation

- [API Documentation](docs/api.md)
- [Configuration Guide](docs/configuration.md)
- [Operations Runbook](docs/runbook.md)
- [Security Policy](SECURITY.md)
- [Contributing Guide](CONTRIBUTING.md)

## License

MIT
