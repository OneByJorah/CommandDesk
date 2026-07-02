# CommandDesk API Documentation

## Overview

CommandDesk exposes several HTTP APIs for interacting with the helpdesk system. All APIs are proxied through Nginx on port 80/443.

## Base URLs

| API | Internal URL | External URL |
|-----|-------------|--------------|
| Helpdesk Agent | `http://helpdesk-agent:8080` | `http://localhost/helpdesk/` |
| Admin Agent | `http://admin-agent:8082` | `http://localhost/admin/` |
| WhatsApp Webhook | `http://whatsapp-webhook:9090` | `http://localhost/webhook/whatsapp` |

---

## Helpdesk Agent API

### Health Check

```
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "agent_mode": "helpdesk",
  "version": "1.0.0",
  "timestamp": 1719000000.0
}
```

### Chat

Send a message to the AI helpdesk agent.

```
POST /chat
Content-Type: application/json
```

**Request Body:**
```json
{
  "session_id": "optional-existing-session-id",
  "user_id": "customer@example.com",
  "message": "I need help with my ticket",
  "platform": "web"
}
```

**Response:**
```json
{
  "session_id": "abc-123-def",
  "response": "I'd be happy to help! Let me look up your tickets...",
  "remaining_requests": 49,
  "session_expires_in": 7100
}
```

**Status Codes:**
- `200 OK` — Success
- `429 Too Many Requests` — Rate limit exceeded
- `422 Unprocessable Entity` — Invalid request body

### Get Session Info

```
GET /session/{session_id}
```

**Response:**
```json
{
  "session_id": "abc-123-def",
  "user_id": "customer@example.com",
  "message_count": 5,
  "request_count": 3,
  "active": true,
  "session_age_seconds": 120,
  "remaining_requests": 47
}
```

---

## Admin Agent API

### Health Check

```
GET /health
```

### Chat (Full Access)

```
POST /chat
Content-Type: application/json
```

Same as helpdesk agent but with full access to all tools including ticket creation.

### List Tickets

```
GET /tickets
```

**Query Parameters:**
- `page` (int, default: 1) — Page number
- `per_page` (int, default: 20) — Items per page
- `status` (string, optional) — Filter by status
- `user_id` (string, optional) — Filter by user

### Cost Analytics

```
GET /costs
```

**Query Parameters:**
- `hours` (int, default: 24) — Lookback period

### System Health

```
GET /system
```

Returns comprehensive system health including all service statuses.

---

## WhatsApp Webhook API

### Webhook Verification (GET)

```
GET /webhook/whatsapp?hub.mode=subscribe&hub.challenge=123456&hub.verify_token=your_token
```

**Response:** Returns the `hub.challenge` value on success.

### Receive Message (POST)

```
POST /webhook/whatsapp
Content-Type: application/json
X-Hub-Signature-256: sha256=...
```

Standard WhatsApp Business API webhook payload.

### Admin: Take Over Conversation

```
POST /admin/takeover/{phone}
```

Pauses the bot for the specified phone number and notifies the customer they're speaking with a human.

### Admin: Resume Bot

```
POST /admin/resume/{phone}
```

Re-enables the bot for the specified phone number.

### Admin: View Queue

```
GET /admin/queue
```

Returns the current human support queue.

**Response:**
```json
{
  "queue": [
    {
      "phone": "+1234567890",
      "waiting_minutes": 3,
      "message": "I need help with my account"
    }
  ],
  "total": 1
}
```

---

## Error Responses

### 429 Rate Limited

```json
{
  "detail": "Rate limit exceeded (50 req/3600s)"
}
```

### 404 Not Found

```json
{
  "detail": "Session not found"
}
```

### 403 Forbidden

```json
{
  "detail": "Invalid signature"
}
```

---

## Rate Limiting

| Limit | Value | Scope |
|-------|-------|-------|
| Requests per session | 50 | Per session |
| Window | 3600 seconds (1 hour) | Sliding window |
| Session duration | 7200 seconds (2 hours) | Max session lifetime |
| Message length | 4000 characters | Per message |
| WhatsApp rate limit | 10 messages/minute | Per phone number |

---

## Authentication

- **Internal APIs**: No authentication required (Docker network only)
- **WhatsApp Webhook**: HMAC-SHA256 signature verification
- **Admin APIs**: IP-restricted to Docker network
- **External access**: Via Nginx with optional TLS

---

## WebSocket (Future)

WebSocket support for real-time ticket updates is planned for a future release.
