"""Tests for the Server class."""

import pytest
from fastapi.testclient import TestClient

from src.server.server import Server


@pytest.fixture
def server():
    """Server instance with test credentials."""
    return Server(api_key_field_name="X-API-Key", api_key="secret")


def test_builder_returns_self(server):
    """use_authenticaton and build return self for chaining."""
    assert server.use_authenticaton() is server
    assert server.build() is server


def test_authenticated_request(server):
    """Request with valid token reaches the route."""
    server.use_authenticaton().build()
    client = TestClient(server.app)
    response = client.get("/health", headers={"X-API-Key": "secret"})
    assert response.status_code == 200


def test_unauthenticated_request(server):
    """Request without token is rejected by middleware."""
    server.use_authenticaton().build()
    client = TestClient(server.app)
    response = client.get("/health")
    assert response.status_code == 401


def test_wrong_token(server):
    """Request with wrong token is rejected by middleware."""
    server.use_authenticaton().build()
    client = TestClient(server.app)
    response = client.get("/health", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401
