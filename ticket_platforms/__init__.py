"""
Ticket platform adapters.

Quick usage:
    from ticket_platforms.registry import register, get, available
"""

from . import osticket
from . import zammad
from . import email
from .registry import register, get, available

__all__ = ["register", "get", "available", "osticket", "zammad", "email"]
