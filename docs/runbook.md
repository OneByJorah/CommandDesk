# CommandDesk Runbook

## Overview

This runbook covers operational procedures for the CommandDesk self-hosted AI helpdesk agent. It is intended for system administrators and operators.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Deployment](#deployment)
3. [Configuration](#configuration)
4. [Monitoring](#monitoring)
5. [Backup & Restore](#backup--restore)
6. [Troubleshooting](#troubleshooting)
7. [Scaling](#scaling)
8. [Security Procedures](#security-procedures)
9. [Disaster Recovery](#disaster-recovery)

## Architecture Overview

CommandDesk consists of the following services:

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| llama.cpp | helpdesk-llama | 8081 | LLM inference (Qwen2.5-7B) |
| Helpdesk Agent | helpdesk-agent | 8080 | Customer-facing AI agent |
| Admin Agent | helpdesk-admin-agent | 8082 | Admin operations & analytics |
| ChromaDB | helpdesk-chroma | 8000 | Vector knowledge base |
| SearXNG | helpdesk-searxng | 8888 | Self-hosted web search |
| n8n | helpdesk-n8n | 5678 | Workflow automation |
| PostgreSQL | helpdesk-postgres | 5432 | Primary database |
| Redis | helpdesk-redis | 6379 | Caching & session store |
| Nginx | helpdesk-nginx | 80/443 | Reverse proxy & security |
| Email Fetcher | helpdesk-email-fetcher | — | IMAP polling |
| WhatsApp Webhook | helpdesk-whatsapp | 9090/8383 | WhatsApp integration |
| Health Monitor | helpdesk-health | — | Service health checks |
| Tools UI | helpdesk-tools-ui | 8484 | Widget & admin panel |

## Deployment

### Prerequisites

- Docker Engine 24+ and Docker Compose v2+
- At least 16GB RAM, 6 CPU cores
- 20GB free disk space (for models + data)

### First-Time Deployment

```bash
# 1. Clone and setup
git clone https://github.com/JorahOne-Services/CommandDesk.git
cd CommandDesk
./scripts/setup.sh

# 2. Configure
cp .env.example .env
# Edit .env with your credentials

# 3. Start all services
docker compose up -d

# 4. Verify
docker compose ps
curl http://localhost:8080/health

# 5. Index knowledge base
docker compose exec helpdesk-agent python3 scripts/index_kb.py
```

### Updating

```bash
# Pull latest code
git pull origin master

# Rebuild and restart
docker compose down
docker compose build --no-cache
docker compose up -d

# Run database migrations if any
docker compose exec postgres psql -U helpdesk -d helpdesk -f /scripts/init-db.sql
```

## Configuration

### Environment Variables

All configuration is done via `.env` file. See `.env.example` for the full list.

**Critical settings:**

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_PASSWORD` | `helpdesk_pass` | PostgreSQL password (CHANGE ME) |
| `REDIS_PASSWORD` | `redis_pass` | Redis password (CHANGE ME) |
| `CHROMA_AUTH_TOKEN` | `chromadb_token_change_me` | ChromaDB auth token (CHANGE ME) |
| `JWT_SECRET` | `jwt_secret_change_me_please` | n8n JWT secret (CHANGE ME) |
| `WHATSAPP_WEBHOOK_SECRET` | `change_me` | WhatsApp webhook secret (CHANGE ME) |
| `RATE_LIMIT_PER_SESSION` | `50` | Max requests per session |
| `MAX_SESSION_DURATION` | `7200` | Max session duration in seconds |

### Config Files

| File | Purpose |
|------|---------|
| `config/hermes-config.yaml` | Helpdesk agent configuration |
| `config/admin-agent-config.yaml` | Admin agent configuration |
| `config/agent-bridge.yaml` | Delegation rules for main Hermes |
| `config/mcp-config.yaml` | Freshdesk MCP configuration |
| `config/nginx.conf` | Nginx reverse proxy configuration |
| `config/searxng-settings.yml` | SearXNG search settings |
| `config/system-prompt.md` | Agent persona/system prompt |

## Monitoring

### Health Checks

Each service exposes a health endpoint:

```bash
# Check all services
make health

# Individual checks
curl http://localhost:8080/health       # Helpdesk agent
curl http://localhost:8082/health       # Admin agent
curl http://localhost:8081/health       # llama.cpp
curl http://localhost:8000/api/v1/heartbeat  # ChromaDB
```

### Logs

```bash
# All services
docker compose logs -f --tail=100

# Specific service
docker compose logs -f helpdesk-agent --tail=50
docker compose logs -f whatsapp-webhook --tail=50
```

### Metrics

The health monitor collects metrics every 30 seconds and stores them in Redis:

```bash
# View latest metrics
docker compose exec redis redis-cli -a $REDIS_PASSWORD get metrics:latest | python3 -m json.tool
```

### Analytics Reports

```bash
# Generate 24-hour report
docker compose exec helpdesk-agent python3 scripts/analytics.py --hours 24

# Generate markdown report
docker compose exec helpdesk-agent python3 scripts/analytics.py --hours 168 --format markdown
```

## Backup & Restore

### PostgreSQL Backup

```bash
# Backup
docker compose exec -T postgres pg_dump -U helpdesk helpdesk > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
cat backup.sql | docker compose exec -T postgres psql -U helpdesk -d helpdesk
```

### Redis Backup

Redis data is persisted via AOF (append-only file) to `redis-data` volume.

### ChromaDB Backup

```bash
# Backup ChromaDB data
tar -czf chroma-backup.tar.gz /path/to/chroma-data
```

### Volume Backups

```bash
# Backup all named volumes
docker run --rm -v commanddesk_postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz -C /data .
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker compose logs <service-name>

# Check if port is in use
sudo lsof -i :8080

# Rebuild from scratch
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

### LLM Not Responding

```bash
# Check llama.cpp health
curl http://localhost:8081/health

# Check model file exists
ls -la models/qwen2.5-7b-instruct-q4_k_m.gguf

# Check resource limits
docker stats helpdesk-llama
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
docker compose exec postgres pg_isready -U helpdesk

# Check PostgreSQL logs
docker compose logs postgres --tail=50

# Reset database
docker compose down -v
docker compose up -d postgres
```

### Redis Issues

```bash
# Test Redis connection
docker compose exec redis redis-cli -a $REDIS_PASSWORD ping

# Check memory usage
docker compose exec redis redis-cli -a $REDIS_PASSWORD info memory
```

### Email Fetcher Not Working

```bash
# Check IMAP connectivity
docker compose logs email-fetcher --tail=50

# Verify IMAP credentials in .env
# Test IMAP connection manually:
openssl s_client -connect imap.example.com:993 -crlf
```

### WhatsApp Webhook Issues

```bash
# Check webhook logs
docker compose logs whatsapp-webhook --tail=50

# Verify webhook URL is accessible from internet
# Check HMAC signature verification
```

## Scaling

### Vertical Scaling

Increase resource limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 4G  # Increase from 2G
      cpus: "4"   # Add CPU cores
```

### Horizontal Scaling

For higher throughput, you can run multiple agent instances behind Nginx:

```yaml
# docker-compose.override.yml
helpdesk-agent:
  deploy:
    replicas: 3
```

### Database Optimization

- Add more RAM to PostgreSQL for larger cache
- Tune `shared_buffers` and `work_mem` in PostgreSQL config
- Add indexes for frequently queried columns

## Security Procedures

### Incident Response

1. **Isolate affected services**: `docker compose stop <service>`
2. **Collect logs**: `docker compose logs --tail=1000 <service> > incident.log`
3. **Check audit log**: Query PostgreSQL audit_log table
4. **Rotate credentials**: Update all secrets in `.env`
5. **Restart**: `docker compose up -d`

### Regular Maintenance

- Weekly: Review audit logs for suspicious activity
- Monthly: Update dependencies (`docker compose build --no-cache`)
- Quarterly: Rotate all secrets and API keys
- Annually: Review and update TLS certificates

### Security Checklist

- [ ] All default passwords changed
- [ ] HTTPS configured with valid TLS certificates
- [ ] Firewall restricts access to ports 80/443 only
- [ ] Rate limiting enabled
- [ ] Audit logging enabled
- [ ] Regular backups configured
- [ ] Docker daemon updated to latest stable
- [ ] Host OS security patches applied

## Disaster Recovery

### Complete System Restore

```bash
# 1. Restore from backup
git clone https://github.com/JorahOne-Services/CommandDesk.git
cd CommandDesk
cp .env.example .env
# Edit .env with your credentials

# 2. Restore database
docker compose up -d postgres
cat backup.sql | docker compose exec -T postgres psql -U helpdesk -d helpdesk

# 3. Restore volumes
docker run --rm -v commanddesk_postgres-data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres-backup.tar.gz -C /data

# 4. Start all services
docker compose up -d

# 5. Verify
make health
```

### Emergency Shutdown

```bash
# Graceful shutdown
docker compose down

# Force shutdown (if hung)
docker compose down --timeout 0
docker compose down -v  # Also removes volumes (DESTRUCTIVE)
```

## Appendix

### Useful Commands

```bash
# Shell access
docker compose exec helpdesk-agent /bin/bash

# PostgreSQL shell
docker compose exec postgres psql -U helpdesk -d helpdesk

# Redis CLI
docker compose exec redis redis-cli -a $REDIS_PASSWORD

# View resource usage
docker stats

# Clean up unused resources
docker system prune -f
```

### Port Reference

| Port | Service | Protocol | Notes |
|------|---------|----------|-------|
| 80 | Nginx | HTTP | Public-facing |
| 443 | Nginx | HTTPS | Public-facing (TLS) |
| 8080 | Helpdesk Agent | HTTP | Internal |
| 8081 | llama.cpp | HTTP | Internal |
| 8082 | Admin Agent | HTTP | Internal |
| 8000 | ChromaDB | HTTP | Internal |
| 5432 | PostgreSQL | TCP | Internal |
| 5678 | n8n | HTTP | Internal |
| 6379 | Redis | TCP | Internal |
| 8484 | Tools UI | HTTP | Internal |
| 8888 | SearXNG | HTTP | Internal |
| 9090 | WhatsApp Webhook | HTTP | Internal |
| 8383 | WhatsApp Webhook | HTTP | External (webhook) |
