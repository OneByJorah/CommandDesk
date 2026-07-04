<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
  <img src="https://img.shields.io/badge/AI-FF6F00?style=for-the-badge&logo=openai&logoColor=white">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge">
</div>

<br>

<div align="center">
  <h1>🎫 CommandDesk</h1>
  <p><strong>Self-Hosted AI Helpdesk Agent</strong></p>
  <p>100% local, AI-powered helpdesk with multi-platform ticketing, knowledge base, and multi-channel communication</p>
  <p>
    <a href="#-features">Features</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-integrations">Integrations</a>
  </p>
</div>

---

## ✨ Features

- **AI-Powered Ticketing** — Auto-respond, triage, and resolve tickets via local LLMs
- **Multi-Platform Support** — osTicket, Freshdesk, Zammad adapters
- **Multi-Channel** — WhatsApp, Email (IMAP), and web interface
- **Knowledge Base** — ChromaDB semantic search for instant answers
- **Admin Dashboard** — Analytics, human takeover, and management
- **Security** — Rate limiting, content filtering, PII detection
- **Workflow Automation** — n8n integration for complex automation
- **Plug-in Architecture** — Extend with custom adapters and tools

## 🚀 Quick Start

```bash
git clone https://github.com/OneByJorah/CommandDesk.git
cd CommandDesk
cp .env.example .env
# Edit .env with your configuration
docker compose up -d
```

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     CommandDesk                          │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐ │
│  │   Ticket    │  │    AI       │  │   Knowledge      │ │
│  │  Platforms  │  │   Engine    │  │     Base         │ │
│  │  osTicket   │  │   Ollama    │  │   ChromaDB       │ │
│  │  Freshdesk  │  │   llama.cpp │  │   Qdrant         │ │
│  │  Zammad     │  │   OpenAI    │  │                  │ │
│  └──────┬──────┘  └──────┬──────┘  └────────┬─────────┘ │
│         │                │                   │           │
│         └────────────────┼───────────────────┘           │
│                          ▼                               │
│              ┌──────────────────────┐                     │
│              │  Communication Layer │                     │
│              │  WhatsApp · Email ·  │                     │
│              │  Web Interface       │                     │
│              └──────────────────────┘                     │
└──────────────────────────────────────────────────────────┘
```

## 📡 Integrations

| Platform | Type | Description |
|----------|------|-------------|
| **osTicket** | Ticketing | Open-source ticket system adapter |
| **Freshdesk** | Ticketing | Cloud-based ticketing |
| **Zammad** | Ticketing | Open-source support system |
| **WhatsApp** | Channel | WhatsApp messaging integration |
| **Email (IMAP)** | Channel | Email-to-ticket conversion |
| **ChromaDB** | Knowledge | Vector search for knowledge base |
| **n8n** | Automation | Workflow automation |

## 🐳 Docker Compose

```bash
# Start with AI engine
docker compose up -d

# Start with development config
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

## 📁 Project Structure

```
CommandDesk/
├── admin/                 # Admin dashboard
├── compose/               # Docker Compose configs
├── config/                # Application configuration
├── scripts/               # Utility scripts
├── skills/                # AI agent skills
├── ticket_platforms/      # osTicket, Freshdesk, Zammad adapters
├── tools-ui/              # Web UI components
├── Dockerfile             # Backend Docker image
├── Dockerfile.email       # Email service image
├── Dockerfile.whatsapp    # WhatsApp service image
├── docker-compose.yml     # Main deployment
├── Makefile               # Build automation
└── requirements.txt       # Python dependencies
```

## 🔒 Security

- Rate limiting on all API endpoints
- Content filtering for malicious payloads
- PII detection and redaction
- Environment-based configuration (`.env` never committed)

## 📄 License

MIT © Jhonattan L. Jimenez

---

<div align="center">
  <p>🤖 AI-powered helpdesk, fully self-hosted</p>
  <p><a href="https://github.com/OneByJorah">@OneByJorah</a></p>
</div>