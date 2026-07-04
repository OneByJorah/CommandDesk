"""
Email-to-ticket adapter for Hermes helpdesk agent.
"""

from __future__ import annotations

from .base import Ticket


class EmailTicketAdapter:
    """
    Non-Ticket adapter: acts as an entrypoint that creates tickets
    in a configured downstream platform.
    """

    def __init__(self, *, imap_host: str, imap_port: int, username: str, password: str, mailbox: str = "INBOX", mark_seen: bool = True, ticket_platform: str = "osticket"):
        self.imap_host = imap_host
        self.imap_port = int(imap_port)
        self.username = username
        self.password = password
        self.mailbox = mailbox
        self.mark_seen = mark_seen
        self.ticket_platform_name = ticket_platform
        self._ticket_platform: Ticket | None = None
