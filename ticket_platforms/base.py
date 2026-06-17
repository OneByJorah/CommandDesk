"""
Base adapter for ticket platforms.
Every adapter must implement create_ticket, update_ticket, search_tickets, close_ticket.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Ticket(ABC):
    @abstractmethod
    def create_ticket(
        self,
        user_id: str,
        subject: str,
        body: str,
        *,
        name: Optional[str] = None,
        email: Optional[str] = None,
        dept_id: Optional[int] = None,
        priority: Optional[str] = None,
        source: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def update_ticket(
        self,
        ticket_id: str,
        status: Optional[str] = None,
        note: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def search_tickets(
        self,
        user_id: str,
        query: str,
        limit: int = 10,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def close_ticket(
        self,
        ticket_id: str,
        reason: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        raise NotImplementedError
