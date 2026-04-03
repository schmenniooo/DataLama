"""Integration tests for rate limiting through the full server stack."""
# pylint: disable=redefined-outer-name

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.middleware.rate_limiting.rate_limiter import RateLimiter
from src.server.server import Server

API_KEY = "test-secret"
HEADERS = {"X-API-Key": API_KEY}

VALID_PAYLOAD = {
    "data_sets": ["date,value\n2024-01-01,100\n2024-01-02,110"],
    "format": "csv",
    "daterange": ["2024-01-01", "2024-12-31"],
}


@pytest.fixture
def mock_redis():
    """Returns a mocked async Redis instance."""
    return AsyncMock()


@pytest.fixture
def client(test_config, mock_redis):
    """TestClient with mocked AI service and mocked Redis."""
    with (
        patch("src.server.server.AiCommunicationService") as mock_service_class,
        patch("src.middleware.rate_limiting.rate_limiter.Redis", return_value=mock_redis),
    ):
        mock_service = mock_service_class.return_value
        mock_service.health_check = AsyncMock(return_value=True)
        mock_service.make_analyse_request = AsyncMock(
            return_value="LLM analysis result"
        )
        server = Server(config=test_config)
        yield TestClient(server.app), mock_redis


def test_first_request_allowed(client):
    """First request through the full stack should succeed."""
    test_client, mock_redis = client
    mock_redis.get.return_value = None

    response = test_client.post("/summary", json=VALID_PAYLOAD, headers=HEADERS)

    assert response.status_code == 200


def test_rate_limited_request_returns_429(client):
    """Request exceeding the limit through the full stack should return 429."""
    test_client, mock_redis = client
    mock_redis.get.return_value = str(RateLimiter.MAX_REQUESTS_PER_MINUTE)

    response = test_client.post("/summary", json=VALID_PAYLOAD, headers=HEADERS)

    assert response.status_code == 429


def test_multiple_requests_within_limit(client):
    """Multiple requests within the limit should all succeed."""
    test_client, mock_redis = client

    for i in range(RateLimiter.MAX_REQUESTS_PER_MINUTE):
        mock_redis.get.return_value = None if i == 0 else str(i)
        response = test_client.post("/summary", json=VALID_PAYLOAD, headers=HEADERS)
        assert response.status_code == 200
