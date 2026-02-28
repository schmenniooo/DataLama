"""Server module for building and running the FastAPI application."""

import uvicorn
from fastapi import FastAPI

from src.api.api import router
from src.middleware.authentication import AuthInterceptor
from src.ollama.ollama import OllamaService
from src.api.api import AnalysisRouter
from src.model.config import Config

# TODO: Add logging
# TODO: Add typing
# TOOD: Comments
# TODO: Tests

class Server:
    """Builds and configures the FastAPI application."""

    def __init__(self, config: Config):
        self.app = FastAPI()
        self.config = config

        self._configure_authenticaton(
            api_key_field_name=config.api_key_field_name, 
            api_key=config.api_key
        )
        ollama_service = self._configure_ollama_service(
            ollama_base_url=config.ollama_base_url, 
            ollama_model=config.ollama_model
        )
        self._configure_analysis_router(ollama_service=ollama_service)

    def _configure_authenticaton(self, api_key_field_name: str, api_key: str):
        """Registers authenticaton interceptor module"""
        auth_middleware = AuthInterceptor(
            api_key_field_name=api_key_field_name,
            api_key=api_key
        ).register_auth_interceptor()
        self.app.add_middleware(auth_middleware)
        return self

    def _configure_ollama_service(self, ollama_base_url: str, ollama_model: str):
        return OllamaService(
            ollama_base_url=ollama_base_url, 
            ollama_model=ollama_model
        )

    def _configure_analysis_router(self, ollama_service: OllamaService):
        """Register routes and return the server instance."""
        analysis_router = AnalysisRouter(ollama_service=ollama_service)
        self.app.include_router(analysis_router)

    def Run(self):
        """Starts uvicorn server"""
        uvicorn.run(
            self.app,
            reload=self.config.debug,
            host=self.config.host,
            port=self.config.port
        )
