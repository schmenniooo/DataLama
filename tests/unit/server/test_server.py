"""Tests for the Server class."""
# pylint: disable=redefined-outer-name

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.server.server import Server


@pytest.fixture
def client(test_config_with_key):
    """TestClient for a configured Server with mocked AiCommunicationService."""
    config = test_config_with_key(api_key="secret")
    with (
        patch("src.server.server.AiCommunicationService") as mock_service_class,
        patch("src.middleware.rate_limiting.rate_limiter.Redis", return_value=AsyncMock()),
    ):
        mock_service = mock_service_class.return_value
        mock_service.health_check = AsyncMock(return_value=True)
        server = Server(config=config)
        yield TestClient(server.app)


@pytest.mark.parametrize("headers,expected_status", [
    ({"X-API-Key": "secret"}, 200),
    ({}, 401),
    ({"X-API-Key": "wrong"}, 401),
], ids=["valid_token", "missing_token", "wrong_token"])
def test_health_endpoint_authentication(client, headers, expected_status):
    """Health endpoint enforces authentication correctly."""
    response = client.get("/health", headers=headers)
    assert response.status_code == expected_status
