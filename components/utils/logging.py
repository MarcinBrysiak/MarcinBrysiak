"""Structured logging setup using loguru.

All modules should get their logger from here:
    from components.utils.logging import get_logger
    logger = get_logger(__name__)

In development: coloured, human-readable output.
In production: JSON lines for log aggregation (Datadog, CloudWatch, etc.).

Never use print() in production code — use logger.info/debug/warning/error.
"""

import sys
from functools import lru_cache

from loguru import logger as _loguru_logger

from config.settings import get_settings


def _configure_logger() -> None:
    settings = get_settings()
    _loguru_logger.remove()

    level = settings.log_level.upper()

    if settings.is_production:
        # JSON for log aggregation
        _loguru_logger.add(
            sys.stdout,
            level=level,
            serialize=True,  # outputs JSON lines
            backtrace=False,
            diagnose=False,
        )
    else:
        # Human-readable for development
        _loguru_logger.add(
            sys.stderr,
            level=level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
                "{message} {extra}"
            ),
            colorize=True,
            backtrace=True,
            diagnose=True,
        )


_configure_logger()


@lru_cache(maxsize=None)
def get_logger(name: str):
    """Return a loguru logger bound to the given module name.

    Usage:
        logger = get_logger(__name__)
        logger.info("event_name", key="value", another_key=123)
    """
    return _loguru_logger.bind(module=name)
