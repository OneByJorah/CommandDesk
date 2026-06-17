"""
osTicket adapter for Hermes helpdesk agent.
"""

from __future__ import annotations

import os
import re
import requests
from typing import Any, Dict, List, Optional

from .base import Ticket
from .registry import register


@register("osticket")
class osTicketAdapter(Ticket):
    def __init__(self, *, base_url: str, api_key: str, dept_id: int = 1, priority: str = "low", source: str = "Web", rate_limit_per_min: int = 5):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.dept_id = dept_id
        self.priority = priority
        self.source = source
        self.rate_limit_per_min = rate_limit_per_min

    def _headers(self):
        return {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    @staticmethod
    def _sanitize(text: str) -> str:
        if not text:
            return ""
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
        return text.strip()

    def _url(self, path: str) -> str:
        return f"{self.base_url}/api/http.php/{path}"

    def create_ticket(self, user_id, subject, body, *, name=None, email=None, dept_id=None, priority=None, source=None, **kwargs):
        subject = self._sanitize(subject)
        body = self._sanitize(body)
        name = name or f"User {user_id}"
        email = email or f"telegram+{user_id}@helpdesk.local"
        payload = {
            "name": name,
            "email": email,
            "phone": "",
            "subject": subject,
            "message": body,
            "ip": "",
            "priority": priority or self.priority,
            "status": "open",
            "deptId": int(dept_id or self.dept_id),
            "source": source or self.source,
        }
        r = requests.post(self._url("tickets.json"), json=payload, headers=self._headers(), timeout=30)
        r.raise_for_status()
        data = r.json()
        ticket = data.get("ticket", {})
        return {"ticket_id": str(ticket.get("ticket_id") or data.get("id", "")), "number": ticket.get("number"), "status": ticket.get("status"), "subject": subject, "platform": "osticket"}

    def update_ticket(self, ticket_id, status=None, note=None, **kwargs):
        payload: Dict[str, Any] = {}
        if status:
            payload["status"] = status
        if note:
            payload["post"] = self._sanitize(note)
            payload["post_status"] = "open"
        r = requests.put(self._url(f"tickets/{ticket_id}.json"), json=payload, headers=self._headers(), timeout=30)
        r.raise_for_status()
        return {"ticket_id": ticket_id, "status": status or "updated", "platform": "osticket"}

    def search_tickets(self, user_id, query, limit=10, **kwargs):
        q = self._sanitize(query)
        r = requests.get(self._url("tickets.json"), params={"query": q, "limit": limit}, headers=self._headers(), timeout=30)
        r.raise_for_status()
        data = r.json()
        tickets = data.get("tickets", []) if isinstance(data, dict) else (data or [])
        return [{"ticket_id": str(t.get("ticket_id") or t.get("id")), "number": t.get("number"), "subject": t.get("subject"), "status": t.get("status")} for t in tickets]

    def close_ticket(self, ticket_id, reason=None, **kwargs):
        payload: Dict[str, Any] = {"status": "closed"}
        if reason:
            payload["post"] = self._sanitize(reason)
            payload["post_status"] = "closed"
        r = requests.put(self._url(f"tickets/{ticket_id}.json"), json=payload, headers=self._headers(), timeout=30)
        r.raise_for_status()
        return {"ticket_id": ticket_id, "status": "closed", "platform": "osticket"}
