"""
Base adapter for ticket platforms.
Every adapter must implement create_ticket, update_ticket, search_tickets, close_ticket.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Ticket(ABC):
    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    def update_ticket(
        self,
        ticket_id: str,
        status: str | None = None,
        note: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def search_tickets(
        self,
        user_id: str,
        query: str,
        limit: int = 10,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def close_ticket(
        self,
        ticket_id: str,
        reason: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        raise NotImplementedError
