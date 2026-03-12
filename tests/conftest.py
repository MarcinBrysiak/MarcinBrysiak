"""Shared pytest fixtures for integration and E2E tests."""

import os

import pytest

# Ensure settings cache is cleared between test sessions
from config.settings import get_settings


@pytest.fixture(autouse=True)
def reset_settings_cache():
    """Clear the settings singleton cache before each test."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def fake_api_key(monkeypatch):
    """Provide a fake Anthropic API key so Settings loads without a real .env."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-000000000000")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
