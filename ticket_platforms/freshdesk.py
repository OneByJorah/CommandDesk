"""
Freshdesk Adapter for Helpdesk Agent
Supports Freshdesk Free Plan (REST API v2)
"""
from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .base import Ticket
from .registry import register


@register("freshdesk")
class FreshdeskAdapter(Ticket):
    """
    Adapter for Freshdesk Free Plan.
    Uses REST API v2 with API key authentication.
    API key is base64 encoded as 'API_KEY:X' for Basic Auth.
    """

    def __init__(self, *, base_url: str, api_key: str, domain: str | None = None):
        """
        Args:
            base_url: Freshdesk URL, e.g. https://yourcompany.freshdesk.com
            api_key: Freshdesk API key
            domain: Freshdesk subdomain (alternative to base_url)
        """
        if domain:
            self.base_url = f"https://{domain}.freshdesk.com"
        else:
            self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.api_url = f"{self.base_url}/api/v2"

    def _get_auth_header(self) -> str:
        """Generate Basic Auth header for Freshdesk API."""
        token = base64.b64encode(f"{self.api_key}:X".encode()).decode()
        return f"Basic {token}"

    def _request(self, path: str, *, method: str = "GET", data: dict | None = None) -> dict[str, Any]:
        """Make an authenticated request to Freshdesk API."""
        url = f"{self.api_url}{path}"
        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json",
        }
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            raise Exception(f"Freshdesk API error {e.code}: {error_body}")

    def create_ticket(
        self,
        user_id: str,
        subject: str,
        body: str,
        *,
        name: str | None = None,
        email: str | None = None,
        dept_id: int | None = None,
        priority: str | None = None,
        source: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new ticket in Freshdesk."""
        data: dict[str, Any] = {
            "subject": subject,
            "description": body,
            "email": email or user_id,
        }
        # Map priority: low=1, normal=2, high=3, urgent=4
        priority_map = {"low": 1, "normal": 2, "medium": 2, "high": 3, "urgent": 4}
        if priority:
            data["priority"] = priority_map.get(priority.lower(), 2)
        if dept_id:
            data["group_id"] = dept_id
        if source:
            data["source"] = 2 if source == "email" else 7  # 2=email, 7=portal

        result = self._request("/tickets", method="POST", data=data)
        return {
            "ticket_id": str(result.get("id")),
            "subject": result.get("subject"),
            "status": "open",
            "url": f"{self.base_url}/helpdesk/tickets/{result.get('id')}",
        }

    def update_ticket(
        self,
        ticket_id: str,
        status: str | None = None,
        note: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Update ticket: add note, change status."""
        data: dict[str, Any] = {}
        # Map status: open=2, pending=3, resolved=4, closed=5
        status_map = {"open": 2, "pending": 3, "resolved": 4, "closed": 5}
        if status:
            data["status"] = status_map.get(status.lower(), 2)

        if note:
            self._request(f"/tickets/{ticket_id}/notes", method="POST", data={
                "body": note,
                "private": False,
            })

        if data:
            self._request(f"/tickets/{ticket_id}", method="PUT", data=data)

        return {"ticket_id": ticket_id, "updated": True}

    def search_tickets(
        self,
        user_id: str,
        query: str,
        limit: int = 10,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Search tickets by user email."""
        # Freshdesk search API
        search_query = f"email:'{user_id}'"
        if query:
            search_query += f" AND \"{query}\""

        try:
            result = self._request(f"/search/tickets?query={urllib.parse.quote(search_query)}")
            tickets = []
            for item in result.get("results", [])[:limit]:
                tickets.append({
                    "ticket_id": str(item.get("id")),
                    "subject": item.get("subject"),
                    "status": item.get("status"),
                    "priority": item.get("priority"),
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                })
            return tickets
        except Exception:
            return []

    def close_ticket(
        self,
        ticket_id: str,
        reason: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Close a ticket (status=5)."""
        data: dict[str, Any] = {"status": 5}
        if reason:
            self._request(f"/tickets/{ticket_id}/notes", method="POST", data={
                "body": f"Closed: {reason}",
                "private": True,
            })
        self._request(f"/tickets/{ticket_id}", method="PUT", data=data)
        return {"ticket_id": ticket_id, "status": "closed", "reason": reason}
