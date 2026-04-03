"""Unit tests for the RateLimiter middleware."""
# pylint: disable=redefined-outer-name

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.middleware.rate_limiting.rate_limiter import RateLimiter


@pytest.fixture
def mock_redis():
    """Returns a mocked async Redis instance."""
    return AsyncMock()


@pytest.fixture
def app(mock_redis):
    """FastAPI app with rate limiting middleware using a mocked Redis."""
    with patch("src.middleware.rate_limiting.rate_limiter.Redis", return_value=mock_redis):
        rate_limiter = RateLimiter()
        test_app = FastAPI()
        test_app.add_middleware(rate_limiter.register_rate_limiter())

        @test_app.get("/test")
        async def test_route():
            return {"result": "ok"}

        return test_app, mock_redis


def test_first_request_passes_and_initializes_counter(app):
    """First request from a new IP should pass through and set the counter in Redis."""
    test_app, mock_redis = app
    mock_redis.get.return_value = None

    client = TestClient(test_app)
    response = client.get("/test")

    assert response.status_code == 200
    mock_redis.set.assert_called_once_with(
        name="testclient",
        value=0,
        ex=RateLimiter.TIME_WINDOW,
    )


def test_request_within_limit_passes(app):
    """Request within the rate limit should pass through and increment the counter."""
    test_app, mock_redis = app
    mock_redis.get.return_value = "5"

    client = TestClient(test_app)
    response = client.get("/test")

    assert response.status_code == 200
    mock_redis.set.assert_called_once_with(
        name="testclient",
        value=6,
        ex=RateLimiter.TIME_WINDOW,
    )


def test_request_at_limit_returns_429(app):
    """Request that hits the rate limit should return 429."""
    test_app, mock_redis = app
    mock_redis.get.return_value = str(RateLimiter.MAX_REQUESTS_PER_MINUTE)

    client = TestClient(test_app)
    response = client.get("/test")

    assert response.status_code == 429


def test_request_over_limit_returns_429(app):
    """Request exceeding the rate limit should return 429."""
    test_app, mock_redis = app
    mock_redis.get.return_value = str(RateLimiter.MAX_REQUESTS_PER_MINUTE + 5)

    client = TestClient(test_app)
    response = client.get("/test")

    assert response.status_code == 429
