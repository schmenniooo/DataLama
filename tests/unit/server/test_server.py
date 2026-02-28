"""Tests for the Server class."""
# pylint: disable=redefined-outer-name

import pytest
from fastapi.testclient import TestClient

from src.server.server import Server
from src.model.config import Config


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
    """TestClient for a configured Server."""
    server = Server(config=config)
    return TestClient(server.app)


def test_authenticated_request(client):
    """Request with valid token reaches the route."""
    response = client.get("/ping", headers={"X-API-Key": "secret"})
    assert response.status_code == 200


def test_unauthenticated_request(client):
    """Request without token is rejected by middleware."""
    response = client.get("/ping")
    assert response.status_code == 401


def test_wrong_token(client):
    """Request with wrong token is rejected by middleware."""
    response = client.get("/ping", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401
