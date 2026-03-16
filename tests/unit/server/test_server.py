"""Tests for the Server class."""
# pylint: disable=redefined-outer-name

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.server.server import Server
from tests.conftest import create_test_config


@pytest.fixture
def client():
    """TestClient for a configured Server with mocked OllamaService."""
    config = create_test_config(api_key="secret")
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
