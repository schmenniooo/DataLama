"""Shared fixtures and constants for integration tests."""
# pylint: disable=redefined-outer-name

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

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
def client(test_config):
    """TestClient with mocked AiCommunicationService."""
    with patch("src.server.server.AiCommunicationService") as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.health_check = AsyncMock(return_value=True)
        mock_service.make_analyse_request = AsyncMock(
            return_value="LLM analysis result"
        )
        server = Server(config=test_config)
        yield TestClient(server.app), mock_service
