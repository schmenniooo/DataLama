"""Integration tests for rate limiting through the full server stack."""

from tests.integration.conftest import HEADERS, VALID_PAYLOAD_CSV

from src.middleware.rate_limiting.rate_limiter import RateLimiter


def test_first_request_allowed(client, mock_redis):
    """First request through the full stack should succeed."""
    test_client, _ = client
    mock_redis.get.return_value = None

    response = test_client.post("/summary", json=VALID_PAYLOAD_CSV, headers=HEADERS)

    assert response.status_code == 200


def test_rate_limited_request_returns_429(client, mock_redis):
    """Request exceeding the limit through the full stack should return 429."""
    test_client, _ = client
    mock_redis.get.return_value = str(RateLimiter.MAX_REQUESTS_PER_MINUTE)

    response = test_client.post("/summary", json=VALID_PAYLOAD_CSV, headers=HEADERS)

    assert response.status_code == 429


def test_multiple_requests_within_limit(client, mock_redis):
    """Multiple requests within the limit should all succeed."""
    test_client, _ = client

    for i in range(RateLimiter.MAX_REQUESTS_PER_MINUTE):
        mock_redis.get.return_value = None if i == 0 else str(i)
        response = test_client.post("/summary", json=VALID_PAYLOAD_CSV, headers=HEADERS)
        assert response.status_code == 200
