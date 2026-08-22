"""
Ticket platform adapters.

Quick usage:
    from ticket_platforms.registry import register, get, available
"""

from . import email, freshdesk, osticket, zammad
from .registry import available, get, register

__all__ = ["register", "get", "available", "osticket", "zammad", "freshdesk", "email"]
