"""Server module for building and running the FastAPI application."""

import uvicorn
from fastapi import FastAPI

from src.middleware.authentication import AuthInterceptor
from src.ollama.ollama import OllamaService
from src.api.api import AnalysisRouter
from src.model.config import Config

# TODO: Add logging
# TODO: Add typing

class Server:
    """Builds and configures the FastAPI application."""

    def __init__(self, config: Config = ""):
        self.app = FastAPI()
        self.config = config

        self._configure_authenticaton()
        ollama_service = self._create_ollama_service()
        self._configure_analysis_router(ollama_service=ollama_service)

    def _configure_authenticaton(self) -> None:
        """Registers authenticaton interceptor module"""
        auth_middleware = AuthInterceptor(
            api_key_field_name=self.config.api_key_field_name,
            api_key=self.config.api_key
        ).register_auth_interceptor()
        self.app.add_middleware(auth_middleware)

    def _create_ollama_service(self) -> OllamaService:
        """Returns new ollama service class"""
        return OllamaService(
            ollama_base_url=self.config.ollama_base_url,
            ollama_model=self.config.ollama_model
        )

    def _configure_analysis_router(self, ollama_service: OllamaService) -> None:
        """Creates new AnalysisRouter class and injects it to FastAPI"""
        analysis_router = AnalysisRouter(ollama_service=ollama_service)
        self.app.include_router(analysis_router.router)

    def Run(self) -> None:
        """Starts uvicorn server"""
        uvicorn.run(
            self.app,
            reload=self.config.debug,
            host=self.config.host,
            port=self.config.port
        )
