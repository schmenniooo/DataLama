"""Shared fixtures and constants for integration tests."""
# pylint: disable=redefined-outer-name

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.model.config.config import Config
from src.server.server import Server

API_KEY = "test-secret"
HEADERS = {"X-API-Key": API_KEY}

VALID_PAYLOAD = {
    "data_sets": ["date,value\n2024-01-01,100\n2024-01-02,110"],
    "format": "csv",
    "daterange": ["2024-01-01", "2024-12-31"],
}

SEPARATOR = "\n---NEW---DATASET---\n"


@pytest.fixture
def client():
    """TestClient with mocked OllamaService."""
    config = Config(
        api_key_field_name="X-API-Key",
        api_key=API_KEY,
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.2",
        debug=False,
        host="0.0.0.0",
        port=3000,
    )
    with patch("src.server.server.OllamaService") as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.health_check = AsyncMock(return_value=True)
        mock_service.make_analyse_request = AsyncMock(
            return_value="LLM analysis result"
        )
        server = Server(config=config)
        yield TestClient(server.app), mock_service
