"""
Registry for ticket platforms.
Adapters register themselves so Hermes can dispatch calls by platform name.
"""

from __future__ import annotations

from typing import Dict, Type

from .base import Ticket


_REGISTRY: Dict[str, Type["Ticket"]] = {}


def register(name: str):
    def decorator(cls: Type[Ticket]):
        _REGISTRY[name.lower()] = cls
        return cls

    return decorator


def get(name: str) -> Type[Ticket]:
    key = name.lower()
    if key not in _REGISTRY:
        raise KeyError(f"Unknown ticket platform: {name}. Registered: {sorted(_REGISTRY)}")
    return _REGISTRY[key]


def available() -> list[str]:
    return sorted(_REGISTRY)
