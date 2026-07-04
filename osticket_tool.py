"""
osTicket tool wrapper for Hermes Agent.
Uses osTicket REST API (v1 HTTP API).
Assumes an API-enabled agent account exists in osTicket.
"""

import os
import re

import requests

OSTICKET_BASE_URL = os.environ.get("OSTICKET_BASE_URL", "").rstrip("/")
OSTICKET_API_KEY = os.environ.get("OSTICKET_API_KEY", "")

DEFAULT_DEPT_ID = int(os.environ.get("OSTICKET_DEFAULT_DEPT_ID", "1"))
DEFAULT_PRIORITY = os.environ.get("OSTICKET_DEFAULT_PRIORITY", "low")
DEFAULT_SOURCE = os.environ.get("OSTICKET_DEFAULT_SOURCE", "Web")
RATE_LIMIT_PER_MIN = int(os.environ.get("OSTICKET_RATE_LIMIT_PER_MIN", "5"))


def _require_config():
    missing = []
    if not OSTICKET_BASE_URL:
        missing.append("OSTICKET_BASE_URL")
    if not OSTICKET_API_KEY:
        missing.append("OSTICKET_API_KEY")
    if missing:
        raise RuntimeError(f"Missing osTicket config: {', '.join(missing)}")


def _headers():
    return {
        "X-API-Key": OSTICKET_API_KEY,
        "Content-Type": "application/json",
    }


def _sanitize(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)               # strip HTML tags
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)  # strip control chars
    return text.strip()


def create_ticket(
    user_id: str,
    subject: str,
    body: str,
    *,
    name: str | None = None,
    email: str | None = None,
    dept_id: int | None = None,
    priority: str | None = None,
    source: str | None = None,
) -> dict:
    """
    Create a ticket in osTicket.
    user_id: Hermes-side identifier (Telegram id, etc.)
    """
    _require_config()
    subject = _sanitize(subject)
    body = _sanitize(body)

    if not name:
        name = f"User {user_id}"
    if not email and user_id:
        email = f"telegram+{user_id}@helpdesk.local"

    payload = {
        "name": name,
        "email": email,
        "phone": "",
        "subject": subject,
        "message": body,
        "ip": "",
        "priority": priority or DEFAULT_PRIORITY,
        "status": "open",
        "deptId": dept_id or DEFAULT_DEPT_ID,
        "source": source or DEFAULT_SOURCE,
    }

    url = f"{OSTICKET_BASE_URL}/api/http.php/tickets.json"
    r = requests.post(url, json=payload, headers=_headers(), timeout=30)
    r.raise_for_status()
    data = r.json()
    ticket = data.get("ticket", {})
    return {
        "ticket_id": str(ticket.get("ticket_id") or data.get("id", "")),
        "number": ticket.get("number"),
        "status": ticket.get("status"),
        "subject": subject,
    }


def update_ticket(ticket_id: str, status: str | None = None, note: str | None = None) -> dict:
    _require_config()
    payload = {}
    if status:
        payload["status"] = status
    if note:
        payload["post"] = _sanitize(note)
        payload["post_status"] = "open"

    url = f"{OSTICKET_BASE_URL}/api/http.php/tickets/{ticket_id}.json"
    r = requests.put(url, json=payload, headers=_headers(), timeout=30)
    r.raise_for_status()
    return {"ticket_id": ticket_id, "status": status or "updated"}


def search_tickets(user_id: str, query: str, limit: int = 10) -> list[dict]:
    _require_config()
    q = _sanitize(query)
    url = f"{OSTICKET_BASE_URL}/api/http.php/tickets.json"
    params = {
        "query": q,
        "limit": limit,
    }
    r = requests.get(url, params=params, headers=_headers(), timeout=30)
    r.raise_for_status()
    data = r.json()
    tickets = data.get("tickets", []) if isinstance(data, dict) else (data or [])
    out = []
    for t in tickets:
        out.append({
            "ticket_id": str(t.get("ticket_id") or t.get("id")),
            "number": t.get("number"),
            "subject": t.get("subject"),
            "status": t.get("status"),
        })
    return out


def close_ticket(ticket_id: str, reason: str | None = None) -> dict:
    _require_config()
    payload = {"status": "closed"}
    if reason:
        payload["post"] = _sanitize(reason)
        payload["post_status"] = "closed"
    url = f"{OSTICKET_BASE_URL}/api/http.php/tickets/{ticket_id}.json"
    r = requests.put(url, json=payload, headers=_headers(), timeout=30)
    r.raise_for_status()
    return {"ticket_id": ticket_id, "status": "closed"}


if __name__ == "__main__":
    # Quick connectivity check (does not require config if vars are set)
    if OSTICKET_BASE_URL and OSTICKET_API_KEY:
        try:
            res = search_tickets("local", "test", limit=1)
            print("osticket API OK, sample:", res[:1])
        except Exception as e:
            print("osticket API check failed:", e)
    else:
        print("Set OSTICKET_BASE_URL and OSTICKET_API_KEY to test.")
