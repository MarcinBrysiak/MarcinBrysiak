"""Retry decorator with exponential backoff for LLM calls.

The Anthropic SDK already retries 429 and 5xx errors automatically
(default max_retries=2). Use this decorator only when you need custom
retry logic — e.g., retrying on structured output validation failures
or application-level errors.

Usage:
    from components.llm.retry import with_retry

    @with_retry(max_attempts=3)
    def call_llm():
        ...
"""

import functools
import time
from typing import Callable, Type

import anthropic

from components.utils.logging import get_logger

logger = get_logger(__name__)

# Errors that are safe to retry
_RETRYABLE = (
    anthropic.RateLimitError,
    anthropic.InternalServerError,
    anthropic.APIConnectionError,
)


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 2.0,
    retryable_exceptions: tuple[Type[Exception], ...] = _RETRYABLE,
) -> Callable:
    """Decorator: retry the wrapped function with exponential backoff.

    Delays: 2s → 4s → 8s (with max_attempts=3, base_delay=2.0)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as exc:
                    last_exc = exc
                    if attempt == max_attempts:
                        break
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        "llm_retry",
                        attempt=attempt,
                        max_attempts=max_attempts,
                        delay_s=delay,
                        error=str(exc),
                        func=func.__name__,
                    )
                    time.sleep(delay)
            raise last_exc  # type: ignore[misc]

        return wrapper

    return decorator
