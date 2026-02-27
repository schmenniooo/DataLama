"""Server module for building and running the FastAPI application."""

import os
from fastapi import FastAPI
from src.api.api import router
from src.middleware.authentication import AuthInterceptor


class Server:
    """Builds and configures the FastAPI application."""

    def __init__(self):
        self.app = FastAPI()

        api_key_field_name = os.getenv("API_KEY_FIELD_NAME", "")
        api_key = os.getenv("API_KEY", "")
        self.auth_interceptor = AuthInterceptor(api_key_field_name=api_key_field_name, api_key=api_key)

    def use_authenticaton(self):
        auth_middleware = self.auth_interceptor.register_auth_middleware()
        self.app.add_middleware(auth_middleware)
        return self

    def build(self):
        """Register routes and return the server instance."""
        self.app.include_router(router)
        return self

    def run(self):
        """Return the configured FastAPI application."""
        return self.app
