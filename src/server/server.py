"""Server module for building and running the FastAPI application."""

import uvicorn
from fastapi import FastAPI

from src.api.api import router
from src.middleware.authentication import AuthInterceptor
from src.ollama.ollama import OllamaService


class Server:
    """Builds and configures the FastAPI application."""

    def __init__(self):
        self.app = FastAPI()

    def use_authenticaton(self, api_key_field_name: str, api_key: str):
        """Registers authenticaton interceptor module"""
        auth_middleware = AuthInterceptor(
            api_key_field_name=api_key_field_name,
            api_key=api_key
        ).register_auth_interceptor()
        self.app.add_middleware(auth_middleware)
        return self

    def setup_ai_model(self, ollama_base_url: str, ollama_model: str):
        ollama_service = OllamaService(
            ollama_base_url=ollama_base_url, 
            ollama_model=ollama_model
        )
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
