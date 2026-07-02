"""
Structured logging configuration for CommandDesk services.
Provides JSON-formatted logging for production and human-readable for development.
"""
from __future__ import annotations

import json
import logging
import logging.config
import os
import sys
import time
from typing import Optional


LOG_FORMAT = os.getenv("LOG_FORMAT", "text")  # "text" or "json"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


class JSONFormatter(logging.Formatter):
    """Format log records as JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }
        # Include extra fields
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        return json.dumps(log_entry)


def setup_logging(name: str, level: Optional[str] = None) -> logging.Logger:
    """Configure and return a structured logger.

    Args:
        name: Logger name (typically __name__)
        level: Override log level (default: LOG_LEVEL env var)

    Returns:
        Configured logger instance
    """
    log_level = (level or LOG_LEVEL).upper()
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if log_level not in valid_levels:
        log_level = "INFO"

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    if LOG_FORMAT == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    logger.addHandler(handler)
    logger.propagate = False

    return logger


def log_with_fields(logger: logging.Logger, level: str, message: str, **fields):
    """Log a message with additional structured fields.

    Args:
        logger: Logger instance
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **fields: Additional key-value pairs to include in the log record
    """
    extra = {"extra_fields": fields}
    getattr(logger, level.lower())(message, extra=extra)
