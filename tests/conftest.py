"""Shared test configuration for all tests."""

import pytest

from src.model.config.config import Config

DEFAULT_API_KEY = "test-secret"


def _create_test_config(api_key: str = DEFAULT_API_KEY) -> Config:
    """Returns a Config instance for testing."""
    return Config(
        api_key_field_name="X-API-Key",
        api_key=api_key,
        model="test-model",
        llm_provider_api_token="test-token",
        debug=False,
        host="0.0.0.0",
        port=3000,
    )


@pytest.fixture
def test_config():
    """Provides a default test Config."""
    return _create_test_config()


@pytest.fixture
def test_config_with_key():
    """Factory fixture for Config with a custom API key."""
    def _factory(api_key: str) -> Config:
        return _create_test_config(api_key=api_key)
    return _factory
