"""Server module for building and running the FastAPI application."""

import logging
import os

import uvicorn
from fastapi import FastAPI

from middleware.rate_limiting.rate_limiter import RateLimiter
from src.api.analysis_router import AnalysisRouter
from middleware.auth.authentication import AuthInterceptor
from src.model.config.config import Config
from src.ai.langchain.communication_service import AiCommunicationService

logger = logging.getLogger("logger")


class Server:  # pylint: disable=too-few-public-methods
    """Builds and configures the FastAPI application."""

    def __init__(self, config: Config):
        self.app = FastAPI()
        self.config = config

        logger.info("Configuring server")

        # Skipping authentication in debug mode
        if not config.debug:
            self._configure_authentication()

        # Connecting to AI provider
        ai_service = self._create_ai_service()

        # Configuring api routes
        self._configure_analysis_router(ai_service=ai_service)

    def _configure_authentication(self) -> None:
        """Registers authentication interceptor module"""
        logger.info("Registering authentication middleware")
        auth_middleware = AuthInterceptor(
            api_key_field_name=self.config.api_key_field_name,
            api_key=self.config.api_key
        ).register_auth_interceptor()
        self.app.add_middleware(auth_middleware)

    def _register_rate_limiter(self) -> None:
        """Registers rate limiter"""
        logger.info("Registering rate limiter")

        redis_host = os.environ.get("REDIS_HOST", "localhost")
        redis_port = int(os.environ.get("REDIS_PORT", 6379))

        rate_limiter = RateLimiter(host=redis_host, port=redis_port).register_rate_limiter()

        self.app.add_middleware(rate_limiter)

    def _create_ai_service(self) -> AiCommunicationService:
        """Returns new AI service class"""
        logger.info(f"Creating AI communication service with {self.config.model}")
        return AiCommunicationService(
            provider=self.config.llm_provider,
            model=self.config.model,
            api_key=self.config.llm_provider_api_token,
        )

    def _configure_analysis_router(self, ai_service: AiCommunicationService) -> None:
        """Creates new AnalysisRouter class and injects it to FastAPI"""
        logger.info("Registering analysis routes")
        analysis_router = AnalysisRouter(ai_service=ai_service)
        self.app.include_router(analysis_router.router)

    def run(self) -> None:
        """Starts uvicorn server"""
        logger.info("Starting server on %s:%s", self.config.host, self.config.port)
        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port
        )
