"""Server module for building and running the FastAPI application."""

import uvicorn
from fastapi import FastAPI

from src.api.api import router
from src.middleware.authentication import AuthInterceptor


class Server:
    """Builds and configures the FastAPI application."""

    def __init__(self, api_key_field_name: str, api_key: str):
        self.app = FastAPI()
        self.auth_interceptor = AuthInterceptor(
            api_key_field_name=api_key_field_name,
            api_key=api_key
        )

    def use_authenticaton(self):
        """Registers authenticaton interceptor module"""
        auth_middleware = self.auth_interceptor.register_auth_interceptor()
        self.app.add_middleware(auth_middleware)
        return self

    def build(self):
        """Register routes and return the server instance."""
        self.app.include_router(router)
        return self

    def run(self, debug: bool, host: str, port: int):
        """Starts uvicorn server"""
        uvicorn.run(
            self.app,
            reload=debug,
            host=host,
            port=port
        )
