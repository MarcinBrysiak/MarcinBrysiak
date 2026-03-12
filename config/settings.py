"""Centralised application settings.

All environment variables are loaded here via Pydantic Settings.
Do not call os.getenv() anywhere else in the codebase — import from here.

Usage:
    from config import get_settings
    settings = get_settings()
    print(settings.anthropic_api_key)
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Anthropic ──────────────────────────────────────────────────────────────
    anthropic_api_key: str = Field(..., description="Anthropic API key")

    # ── Application ───────────────────────────────────────────────────────────
    app_env: Literal["development", "staging", "production"] = "development"
    log_level: Literal["debug", "info", "warning", "error"] = "info"

    # ── LLM defaults ──────────────────────────────────────────────────────────
    default_model: str = "claude-opus-4-6"
    default_max_tokens: int = 4096

    # ── Feature flags ─────────────────────────────────────────────────────────
    feature_content_writer: bool = True
    feature_campaign_analyst: bool = False
    feature_lead_scorer: bool = False
    feature_agent_monitor_dashboard: bool = True

    # ── Dashboard ─────────────────────────────────────────────────────────────
    streamlit_port: int = 8501

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton Settings instance.

    Cached after first call — settings are read once at startup.
    Call get_settings.cache_clear() in tests to reset.
    """
    return Settings()
