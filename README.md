# CommandDesk

> Self-hosted AI helpdesk agent with multi-platform ticketing and live cost tracking.

![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/status-active-%23FFB300?style=for-the-badge)
![Language](https://img.shields.io/badge/language-Python-informational?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-linux-informational?style=for-the-badge)

CommandDesk is an enterprise-grade, ops-precise platform built for VIDE and SMB operations. Run it solo. Deliver results.

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

| Layer | Stack |
|---|---|
| Runtime | Python |
| Environment | Linux |
| VCS | Git + GitHub |

## Quickstart

```bash
git clone https://github.com/OneByJorah/CommandDesk.git
cd CommandDesk
docker compose up -d
```
Verify at `http://<host-ip>`.

## Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| (see Environment Variables) | — | — | — |

For full details, see the in-repo [Environment Variables](#environment-variables) section.

## Roadmap

- Feature parity with production requirements
- Observability and alerting expansions
- Community feedback integration

## License

MIT — Copyright JorahOne, LLC. See [LICENSE](LICENSE) for details.

---

[OneByJorah](https://github.com/OneByJorah) · [JorahOne-Services](https://github.com/JorahOne-Services)
