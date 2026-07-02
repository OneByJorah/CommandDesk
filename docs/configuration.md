# CommandDesk Configuration Guide

## Overview

CommandDesk is configured through a combination of environment variables (`.env`), YAML configuration files (`config/`), and Docker Compose overrides.

---

## Environment Variables (`.env`)

Copy `.env.example` to `.env` and fill in your values.

### LLM Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LLAMA_MODEL_PATH` | `/models/qwen2.5-7b-instruct-q4_k_m.gguf` | Path to GGUF model file |
| `LLAMA_PORT` | `8081` | llama.cpp server port |
| `LLAMA_CTX_SIZE` | `65536` | Context window size |
| `LLAMA_THREADS` | `6` | CPU threads for inference |

### Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `postgres` | PostgreSQL hostname |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `helpdesk` | Database name |
| `DB_USER` | `helpdesk` | Database user |
| `DB_PASSWORD` | `change...n` | **CHANGE THIS** |

### Redis Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | `redis` | Redis hostname |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_PASSWORD` | `change...n` | **CHANGE THIS** |

### Email (IMAP) Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `IMAP_HOST` | `imap.example.com` | IMAP server hostname |
| `IMAP_PORT` | `993` | IMAP port (SSL) |
| `IMAP_USER` | `helpdesk@example.com` | IMAP username |
| `IMAP_PASSWORD` | `change...n` | **CHANGE THIS** |
| `POLL_INTERVAL` | `60` | Polling interval in seconds |
| `TICKET_PLATFORM` | `osticket` | Target ticket platform |

### Ticket Platform Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OSTICKET_URL` | `https://support.example.com/api/tickets.json` | osTicket API URL |
| `OSTICKET_API_KEY` | `change...n` | osTicket API key |
| `FRESHDESK_URL` | `https://yourcompany.freshdesk.com` | Freshdesk domain |
| `FRESHDESK_API_KEY` | `change...n` | Freshdesk API key |

### Security & Rate Limiting

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_PER_SESSION` | `50` | Max requests per session |
| `RATE_LIMIT_WINDOW` | `3600` | Rate limit window (seconds) |
| `MAX_MESSAGE_LENGTH` | `4000` | Max message length (chars) |
| `MAX_SESSION_DURATION` | `7200` | Max session duration (seconds) |
| `CHROMA_AUTH_TOKEN` | `chromadb_token_change_me` | ChromaDB auth token |
| `JWT_SECRET` | `jwt_secret_change_me_please` | n8n JWT secret |
| `WHATSAPP_WEBHOOK_SECRET` | `change_me` | WhatsApp webhook secret |

### WhatsApp Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `WHATSAPP_TOKEN` | — | WhatsApp Business API token |
| `WHATSAPP_PHONE_NUMBER_ID` | — | WhatsApp phone number ID |
| `WHATSAPP_WEBHOOK_SECRET` | `change_me` | Webhook verification token |
| `ADMIN_PHONE_NUMBER` | — | Admin's WhatsApp number |
| `WHATSAPP_RATE_LIMIT_PER_MINUTE` | `10` | Rate limit per phone/minute |

---

## YAML Configuration Files

### `config/hermes-config.yaml`

Helpdesk agent configuration:

```yaml
agent:
  name: "J1 Helpdesk Agent"
  mode: helpdesk
  allow_create_ticket: false

llm:
  provider: openai-compatible
  base_url: http://llama:8081/v1
  model: qwen2.5-7b-instruct
  max_tokens: 2048
  temperature: 0.3

knowledge_base:
  provider: chromadb
  url: http://chroma:8000
  collection: helpdesk-kb

search:
  provider: searxng
  url: http://searxng:8080

rate_limiting:
  max_requests_per_session: 50
  window_seconds: 3600
  max_message_length: 4000
  max_session_duration: 7200
```

### `config/admin-agent-config.yaml`

Admin agent configuration (same structure but with `allow_create_ticket: true`).

### `config/agent-bridge.yaml`

Delegation rules for connecting to a main Hermes Agent instance:

```yaml
bridges:
  helpdesk-agent:
    url: "http://helpdesk-agent:8080"
    triggers: ["ticket", "helpdesk", "support", "my issue"]
  admin-agent:
    url: "http://admin-agent:8082"
    triggers: ["admin", "manage tickets", "cost analytics"]
```

### `config/mcp-config.yaml`

Freshdesk MCP server configuration:

```yaml
mcp_servers:
  freshdesk:
    command: "python"
    args: ["-m", "freshdesk_mcp"]
    env:
      FRESHDESK_DOMAIN: "${FRESHDESK_DOMAIN}"
      FRESHDESK_API_KEY: "${FRESHDESK_API_KEY}"
```

### `config/nginx.conf`

Nginx reverse proxy configuration with security headers, rate limiting, and TLS support.

### `config/searxng-settings.yml`

SearXNG search engine configuration. Configure which search engines to use and their priorities.

### `config/system-prompt.md`

The system prompt that defines the AI agent's persona, behavior, and constraints.

---

## Docker Compose Configuration

### Production (`docker-compose.yml`)

Full production stack with all services.

### Development (`docker-compose.dev.yml`)

Development overrides with hot-reload, debug ports, and relaxed security.

### Production Override (`docker-compose.prod.yml`)

Production-specific settings (resource limits, logging drivers, etc.).

### Compose Extensions (`compose/`)

Modular compose files for specific features:

| File | Purpose |
|------|---------|
| `compose/docker-compose.mail.yml` | Email services |
| `compose/docker-compose.monitoring.yml` | Monitoring stack |
| `compose/docker-compose.storage.yml` | Storage services |
| `compose/docker-compose.ci.yml` | CI/CD services |
| `compose/docker-compose.automation.yml` | Automation services |
| `compose/docker-compose.knowledge.yml` | Knowledge base services |
| `compose/docker-compose.selfhosted.yml` | Self-hosted services |
| `compose/docker-compose.wiki.yml` | Wiki services |
| `compose/docker-compose.plus.yml` | Premium services |
| `compose/docker-compose.git.yml` | Git services |

---

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make setup` | One-time setup |
| `make start` | Start all services |
| `make stop` | Stop all services |
| `make restart` | Restart all services |
| `make rebuild` | Rebuild and restart |
| `make logs` | View all logs |
| `make health` | Check service health |
| `make index-kb` | Index knowledge base |
| `make dev` | Start in development mode |
| `make shell` | Open shell in agent container |
| `make psql` | Open PostgreSQL shell |
| `make redis-cli` | Open Redis CLI |
| `make test-api` | Test agent API |
| `make clean` | Remove containers and volumes |
| `make clean-data` | Remove all data (DANGEROUS) |

---

## Advanced Configuration

### Custom LLM Models

1. Download a GGUF model to `models/`
2. Update `LLAMA_MODEL_PATH` in `.env`
3. Update `LLM_MODEL` in `.env`
4. Restart: `docker compose restart llama helpdesk-agent`

### Custom System Prompt

Edit `config/system-prompt.md` to customize the agent's behavior, tone, and capabilities.

### Adding Ticket Platforms

1. Create a new adapter in `ticket_platforms/` extending `BasePlatform`
2. Register it in `ticket_platforms/registry.py`
3. Add configuration variables to `.env`
4. Update `docker-compose.yml` if new services are needed

### Custom Workflows

Place n8n workflow JSON files in `workflows/`. They will be automatically loaded by n8n on startup.
