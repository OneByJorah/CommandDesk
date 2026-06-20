# J1 Helpdesk Agent

**Self-hosted AI helpdesk with multi-platform ticketing, email-to-ticket, knowledge base, and a plug-in agent architecture.**

100% local and free. Compatible with Hermes Agent and the broader agent-skills ecosystem.

## Features

- 🤖 **AI Helpdesk Agent** — Answers customer questions, searches tickets, updates status
- 🔌 **Plug-in Architecture** — Main Hermes can delegate to helpdesk agent or admin agent
- 📧 **Email-to-Ticket** — IMAP polling creates tickets automatically
- 🎫 **Multi-Platform** — osTicket, Freshdesk (free plan), Zammad adapters
- 📚 **Knowledge Base** — ChromaDB-powered semantic search
- 🔍 **Web Search** — Self-hosted SearXNG
- 📊 **Admin Dashboard** — Cost tracking, session monitoring, audit log
- 🛡️ **Security** — Rate limiting, session limits, content filtering, audit logging
- 🔄 **Workflow Automation** — n8n for escalation, notifications

## Architecture

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
    │  Nginx (80/443)    │  Email Fetcher            │
    └────────────────────────────────────────────────┘
```

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

**End users CANNOT create tickets via the AI agent.** Tickets are created via:
- Email (IMAP polling)
- osTicket web portal
- Freshdesk web portal

## Quick Start

```bash
# 1. Clone
git clone https://github.com/OneByJorah/CommandDesk.git
cd CommandDesk

# 2. Run setup
./scripts/setup.sh

# 3. Configure
cp .env.example .env
# Edit .env with your IMAP credentials and ticket platform settings

# 4. Start
docker compose up -d

# 5. Index knowledge base
docker compose exec helpdesk-agent python3 scripts/index_kb.py

# 6. Open
# Dashboard: http://localhost/dashboard/
# Helpdesk API: http://localhost/helpdesk/health
# Admin API: http://localhost/admin/health
# n8n: http://localhost:5678
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
| `LLM_MODEL` | qwen2.5-7b-instruct | LLM model name |

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

When the main Hermes detects a helpdesk-related intent, it delegates to the helpdesk agent and returns the response.

## Ticket Platforms

| Platform | Status | Adapter |
|----------|--------|---------|
| osTicket | ✅ Full | `ticket_platforms/osticket.py` |
| Freshdesk (free) | ✅ Full | `ticket_platforms/freshdesk.py` |
| Zammad | ✅ Full | `ticket_platforms/zammad.py` |
| Email (IMAP) | ✅ Full | `ticket_platforms/email.py` |

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

## Adding Knowledge Base Articles

1. Place `.md` or `.txt` files in `knowledge-base/`
2. Run: `docker compose exec helpdesk-agent python3 scripts/index_kb.py`
3. Agent will automatically find and cite them

## Monitoring

- **Admin Dashboard**: `http://localhost/dashboard/`
- **n8n Workflows**: `http://localhost:5678`
- **Logs**: `docker compose logs -f helpdesk-agent`

## Resource Requirements

| Service | RAM Limit | CPU |
|---------|-----------|-----|
| llama.cpp (7B Q4) | 7GB | 6 cores |
| Hermes Agent | 2GB | 2 cores |
| ChromaDB | 2GB | 2 cores |
| PostgreSQL | 1GB | 1 core |
| Redis | 300MB | 1 core |
| Others | ~2GB | shared |
| **Total** | **~14GB** | **6 cores** |

## License

MIT
