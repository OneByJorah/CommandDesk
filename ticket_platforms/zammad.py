"""
Zammad adapter for Hermes helpdesk agent.
"""

from __future__ import annotations

from typing import Any

import requests

from .base import Ticket
from .registry import register


@register("zammad")
class ZammadAdapter(Ticket):
    def __init__(self, *, base_url: str, api_token: str, group_id: int | None = None, priority_id: int = 2, state_id: int = 1):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.group_id = group_id
        self.priority_id = priority_id
        self.state_id = state_id

    def _headers(self):
        return {"Authorization": f"Token token={self.api_token}", "Content-Type": "application/json"}

    def _url(self, path: str) -> str:
        return f"{self.base_url}/api/v1/{path}"

    def create_ticket(self, user_id, subject, body, *, name=None, email=None, priority=None, source=None, **kwargs):
        customer = email or f"telegram+{user_id}@helpdesk.local"
        payload = {
            "title": subject,
            "group_id": self.group_id or 1,
            "priority_id": self.priority_id,
            "state_id": self.state_id,
            "article": {"type": "text", "body": body or subject, "internal": False},
            "customer": customer,
        }
        if name:
            payload["customer"] = {"firstname": name, "email": customer}
        r = requests.post(self._url("tickets"), json=payload, headers=self._headers(), timeout=30)
        r.raise_for_status()
        data = r.json()
        return {"ticket_id": str(data.get("id")), "number": data.get("number"), "status": data.get("state", {}).get("name"), "subject": subject, "platform": "zammad"}

    def update_ticket(self, ticket_id, status=None, note=None, **kwargs):
        payload: dict[str, Any] = {}
        if status:
            payload["state"] = status
        if note:
            payload["article"] = {"type": "text", "body": note, "internal": bool(kwargs.get("internal", False))}
        r = requests.patch(self._url(f"tickets/{ticket_id}"), json=payload, headers=self._headers(), timeout=30)
        r.raise_for_status()
        return {"ticket_id": ticket_id, "status": status or "updated", "platform": "zammad"}

    def search_tickets(self, user_id, query, limit=10, **kwargs):
        q = f"{query} user:{user_id}"
        r = requests.get(self._url("tickets/search"), params={"query": q, "per_page": limit}, headers=self._headers(), timeout=30)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list):
            tickets = data
        elif isinstance(data, dict):
            tickets = data.get("tickets", data.get("assets", []))
        else:
            tickets = []
        return [{"ticket_id": str(t.get("id")), "number": t.get("number"), "subject": t.get("title"), "status": (t.get("state") or {}).get("name") if isinstance(t.get("state"), dict) else t.get("state")} for t in tickets]

    def close_ticket(self, ticket_id, reason=None, **kwargs):
        payload: dict[str, Any] = {"state": "closed"}
        if reason:
            payload["article"] = {"type": "text", "body": reason, "internal": True}
        r = requests.patch(self._url(f"tickets/{ticket_id}"), json=payload, headers=self._headers(), timeout=30)
        r.raise_for_status()
        return {"ticket_id": ticket_id, "status": "closed", "platform": "zammad"}
