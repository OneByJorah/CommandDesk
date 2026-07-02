"""
Error handling utilities for CommandDesk services.
Provides consistent error handling, retry logic, and error reporting.
"""
from __future__ import annotations

import asyncio
import functools
import logging
import time
from typing import Any, Callable, Optional, Type, TypeVar

T = TypeVar("T")

logger = logging.getLogger(__name__)


class ServiceError(Exception):
    """Base exception for service-level errors."""

    def __init__(self, message: str, service: str = "unknown", status_code: int = 500):
        self.service = service
        self.status_code = status_code
        super().__init__(message)


class ConfigurationError(ServiceError):
    """Raised when required configuration is missing or invalid."""

    def __init__(self, message: str, config_key: str = ""):
        self.config_key = config_key
        super().__init__(message, service="configuration", status_code=500)


class DatabaseError(ServiceError):
    """Raised on database connection or query failures."""

    def __init__(self, message: str, query: str = ""):
        self.query = query
        super().__init__(message, service="database", status_code=503)


class ExternalServiceError(ServiceError):
    """Raised when an external service (LLM, API, etc.) fails."""

    def __init__(self, message: str, service: str = "external", status_code: int = 502):
        super().__init__(message, service=service, status_code=status_code)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None,
):
    """Decorator for retrying async functions with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional callback called with (attempt, exception) on each retry

    Usage:
        @retry(max_attempts=3, delay=1.0)
        async def fetch_data():
            return await client.get(url)
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        if on_retry:
                            on_retry(attempt, e)
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed for "
                            f"{func.__name__}: {e}. Retrying in {current_delay}s..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for "
                            f"{func.__name__}: {e}"
                        )

            raise last_exception  # type: ignore[misc]
        return wrapper
    return decorator


def require_env(var_name: str) -> str:
    """Get a required environment variable or raise ConfigurationError.

    Args:
        var_name: Name of the environment variable

    Returns:
        The value of the environment variable

    Raises:
        ConfigurationError: If the variable is not set or empty
    """
    import os
    value = os.getenv(var_name)
    if not value:
        raise ConfigurationError(
            f"Required environment variable {var_name} is not set",
            config_key=var_name,
        )
    return value


def safe_get_env(var_name: str, default: str = "") -> str:
    """Safely get an environment variable with a default.

    Args:
        var_name: Name of the environment variable
        default: Default value if not set

    Returns:
        The value or default
    """
    import os
    return os.getenv(var_name, default)


def format_error_response(error: Exception, include_traceback: bool = False) -> dict:
    """Format an exception into a standardized error response dict.

    Args:
        error: The exception to format
        include_traceback: Whether to include traceback info

    Returns:
        Dict with error details suitable for API responses
    """
    import traceback

    response = {
        "error": type(error).__name__,
        "message": str(error),
    }

    if isinstance(error, ServiceError):
        response["service"] = error.service
        response["status_code"] = error.status_code

    if include_traceback:
        response["traceback"] = traceback.format_exc()

    return response
