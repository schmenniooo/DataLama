"""Tests for the Server class."""
# pylint: disable=redefined-outer-name

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.server.server import Server
from src.model.config.config import Config


@pytest.fixture
def config():
    """Test configuration."""
    return Config(
        api_key_field_name="X-API-Key",
        api_key="secret",
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.2",
        debug=False,
        host="0.0.0.0",
        port=3000,
    )


@pytest.fixture
def client(config):
    """TestClient for a configured Server with mocked OllamaService."""
    with patch("src.server.server.OllamaService") as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.health_check = AsyncMock(return_value=True)
        server = Server(config=config)
        yield TestClient(server.app)


def test_authenticated_request(client):
    """Request with valid token reaches the route."""
    response = client.get("/health", headers={"X-API-Key": "secret"})
    assert response.status_code == 200


def test_unauthenticated_request(client):
    """Request without token is rejected by middleware."""
    response = client.get("/health")
    assert response.status_code == 401


def test_wrong_token(client):
    """Request with wrong token is rejected by middleware."""
    response = client.get("/health", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401
