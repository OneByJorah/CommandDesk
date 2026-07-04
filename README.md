<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
  <img src="https://img.shields.io/badge/AI-FF6F00?style=for-the-badge&logo=openai&logoColor=white">
</div>

<br>

<div align="center">
  <h1>🎫 CommandDesk</h1>
  <p><strong>Self-Hosted AI Helpdesk Agent</strong></p>
  <p>100% local, free AI-powered helpdesk with multi-platform ticketing, knowledge base, and multi-channel communication</p>
  <p>
    <a href="#-features">Features</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-integrations">Integrations</a>
  </p>
</div>

---

## ✨ Features

- **AI-Powered Ticketing** — Auto-respond, triage, and resolve tickets via AI
- **Multi-Platform Support** — osTicket, Freshdesk, Zammad adapters
- **Multi-Channel** — WhatsApp, Email (IMAP), and web interface
- **Knowledge Base** — ChromaDB semantic search for instant answers
- **Admin Dashboard** — Analytics, human takeover, and management
- **Security** — Rate limiting, content filtering, PII detection
- **Workflow Automation** — n8n integration for complex workflows
- **Plug-in Architecture** — Extend with custom adapters and tools

## 🚀 Quick Start

```bash
git clone https://github.com/OneByJorah/CommandDesk.git
cd CommandDesk
docker-compose up -d
```

## 🏗️ Architecture

```
CommandDesk/
├── admin/                    # Admin dashboard
├── compose/                  # Docker Compose configs
├── config/                   # Application configuration
├── scripts/                  # Utility scripts
├── skills/                   # AI agent skills
├── ticket_platforms/         # osTicket, Freshdesk, Zammad
├── tools-ui/                 # Web UI components
├── workflows/                # n8n workflow definitions
├── Dockerfile                # Backend Docker image
├── docker-compose.yml        # Main deployment
└── requirements.txt          # Python dependencies
```

## 📡 Integrations

| Platform | Type | Description |
|----------|------|-------------|
| osTicket | Ticketing | Open-source ticket system adapter |
| Freshdesk | Ticketing | Cloud-based ticketing |
| Zammad | Ticketing | Open-source support system |
| WhatsApp | Channel | WhatsApp messaging |
| Email | Channel | IMAP email-to-ticket |
| ChromaDB | Knowledge | Vector search for KB |

## 📄 License

MIT © Jhonattan L. Jimenez

---

<div align="center">
  <p>🤖 Your AI helpdesk, fully self-hosted</p>
  <p><a href="https://github.com/OneByJorah">@OneByJorah</a></p>
</div>
