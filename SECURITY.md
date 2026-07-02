# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

We take the security of CommandDesk seriously. If you believe you have found a security vulnerability, please report it to us as described below.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to **security@jorahone.com** (or the repository owner's security contact).

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

### What to include

- Type of issue (e.g., SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### What to expect

- You will receive an acknowledgment of your report within 48 hours
- We will confirm the issue and determine its severity
- We will work on a fix and release it as soon as possible
- We will notify you when the fix is released

## Security Best Practices

### For Production Deployments

1. **Change all default secrets** — Update `REDIS_PASSWORD`, `DB_PASSWORD`, `CHROMA_AUTH_TOKEN`, `JWT_SECRET`, and `WHATSAPP_WEBHOOK_SECRET` in your `.env` file
2. **Use HTTPS** — Configure TLS certificates for Nginx (see `config/nginx.conf`)
3. **Restrict network access** — Internal services bind to `127.0.0.1` by default; do not expose them publicly
4. **Keep dependencies updated** — Run `docker compose build --no-cache` after updating `requirements.txt`
5. **Enable rate limiting** — Default limits are conservative; adjust `RATE_LIMIT_PER_SESSION` as needed
6. **Audit logs** — All requests are logged to PostgreSQL; monitor for suspicious activity
7. **WhatsApp webhook** — HMAC signature verification is enabled; keep `WHATSAPP_WEBHOOK_SECRET` secret

### Docker Security

- Containers run with read-only root filesystems where possible
- Services bind to localhost (`127.0.0.1`) unless explicitly required
- Non-root users are used inside containers
- Secrets are passed via environment variables, never hardcoded

## Known Security Features

- **Rate Limiting**: 50 requests/session/hour (configurable)
- **Session Duration**: 2-hour max per session
- **Message Length**: 4000 chars max
- **Content Filter**: Blocks password/credit_card/SSN in responses
- **Audit Log**: All requests logged to PostgreSQL
- **Network**: Internal services bound to 127.0.0.1
- **Admin Agent**: IP-whitelisted (Docker network only)
- **Nginx**: Security headers, request size limits, rate zones
- **WhatsApp**: HMAC signature verification
