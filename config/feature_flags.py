"""Feature flag helpers.

Usage:
    from config.feature_flags import require_feature, is_enabled

    @require_feature("content_writer")
    def run_content_writer():
        ...

    if is_enabled("campaign_analyst"):
        ...
"""

import functools
from typing import Callable

from config.settings import get_settings


def is_enabled(flag_name: str) -> bool:
    """Return True if the named feature flag is enabled."""
    settings = get_settings()
    attr = f"feature_{flag_name}"
    if not hasattr(settings, attr):
        raise ValueError(f"Unknown feature flag: '{flag_name}'. Add it to Settings first.")
    return getattr(settings, attr)


def require_feature(flag_name: str) -> Callable:
    """Decorator — raises RuntimeError if the feature flag is not enabled."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not is_enabled(flag_name):
                raise RuntimeError(
                    f"Feature '{flag_name}' is disabled. "
                    f"Set FEATURE_{flag_name.upper()}=true in your .env to enable it."
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator
