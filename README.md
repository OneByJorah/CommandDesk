<!-- j1-brand:v2 -->
<div align="center">

# CommandDesk

A self-hosted, 100% local AI helpdesk agent — multi-platform ticketing, email-to-ticket ingestion, admin dashboard with live cost tracking.

[![GitHub](https://img.shields.io/badge/github-OneByJorah%2FCommandDesk-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://github.com/OneByJorah/CommandDesk)
[![License](https://img.shields.io/badge/license-MIT-FFB300?style=for-the-badge&labelColor=0d0d0c)](LICENSE)
[![Language](https://img.shields.io/badge/Python-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://python.org)
[![Built by](https://img.shields.io/badge/built%20by-JorahOne%20LLC-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://github.com/OneByJorah)

</div>

---

## Why This Exists

Managed helpdesks nickel-and-dime you per agent, per ticket, per integration. CommandDesk is a fully local alternative that runs LLMs (Ollama, llama.cpp, or OpenAI-compatible), connects to osTicket, Freshdesk, and Zammad, ingests email via IMAP, and gives you an admin dashboard with real-time cost tracking — all behind `docker compose up`.

## Key Features

| Feature | Why It Matters |
|---|---|
| AI-powered auto-response & triage | Local LLMs resolve tickets without sending data to third parties |
| Multi-platform ticketing | osTicket, Freshdesk, and Zammad support in one deploy |
| Email-to-ticket (IMAP) | Converts inbound email into tickets automatically |
| WhatsApp integration | Lets users file and track tickets via WhatsApp |
| Vector knowledge base (ChromaDB) | Semantic search across your documentation for accurate answers |
| n8n workflow integration | Chain helpdesk events into automations |
| PII detection & rate limiting | Built-in safety layers before responses reach customers |

## Quick Start

```bash
git clone https://github.com/OneByJorah/CommandDesk.git
cd CommandDesk
cp .env.example .env   # configure your LLM backend, ticketing platform, etc.
docker compose up -d
```

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Ticketing    │◀───▶│  CommandDesk  │────▶│  AI Engine    │
│  osTicket     │     │  FastAPI      │     │  Ollama /     │
│  Freshdesk    │     │  Admin UI     │     │  llama.cpp    │
│  Zammad       │     │  Web UI       │     │  OpenAI API   │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                     ┌──────▼───────┐
                     │  ChromaDB     │
                     │  (vector KB)  │
                     └──────────────┘
```

## Documentation

| Doc | Description |
|---|---|
| [Setup Guide](docs/setup.md) | Configuration and first-run walkthrough |
| [Platform Integration](docs/platforms.md) | Connecting osTicket, Freshdesk, and Zammad |
| [AI Configuration](docs/ai.md) | Choosing and tuning your LLM backend |

---

## License

MIT © JorahOne, LLC — see [LICENSE](LICENSE)

<sub>Part of the JorahOne infrastructure ecosystem.</sub>
