"""Tests for the AuthInterceptor middleware."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.middleware.authentication import AuthInterceptor


@pytest.fixture
def app():
    """FastAPI app with auth middleware applied."""
    test_app = FastAPI()
    interceptor = AuthInterceptor(api_key_field_name="X-API-Key", api_key="secret")
    test_app.add_middleware(interceptor.register_auth_interceptor())

    @test_app.get("/test")
    async def test_route():
        return {"result": "ok"}

    return test_app


def test_valid_token(app):
    """Request with correct token passes through."""
    client = TestClient(app)
    response = client.get("/test", headers={"X-API-Key": "secret"})
    assert response.status_code == 200


def test_invalid_token(app):
    """Request with wrong token returns 401."""
    client = TestClient(app)
    response = client.get("/test", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


def test_missing_token(app):
    """Request without token returns 401."""
    client = TestClient(app)
    response = client.get("/test")
    assert response.status_code == 401


def test_missing_config():
    """Missing api_key_field_name or api_key returns 401."""
    test_app = FastAPI()
    interceptor = AuthInterceptor(api_key_field_name=None, api_key=None)
    test_app.add_middleware(interceptor.register_auth_interceptor())

    @test_app.get("/test")
    async def test_route():
        return {"result": "ok"}

    client = TestClient(test_app)
    response = client.get("/test")
    assert response.status_code == 401
