"""Server module for building and running the FastAPI application."""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI

from src.ai.langchain.communication_service import AiCommunicationService
from src.api.analysis_router import AnalysisRouter
from src.middleware.auth.authentication import AuthInterceptor
from src.middleware.rate_limiting.rate_limiter import RateLimiter
from src.model.config.config import Config

logger = logging.getLogger("logger")


class Server:  # pylint: disable=too-few-public-methods
    """Builds and configures the FastAPI application."""

    def __init__(self, config: Config):
        logger.info("Configuring server")
        self.config = config

        # Skipping authentication in debug mode
        if not config.debug:
            self._configure_authentication()

        # Create rate limiter first (needed by lifespan when creating FastAPI instance)
        self.rate_limiter = self._configure_rate_limiter()

        # Creating FastAPI instance and registering auto redis flush
        self.app = FastAPI(lifespan=lambda app: self._rate_limiting_redis_lifecycle(app))

        # Registering rate limiter middleware
        self.app.add_middleware(self.rate_limiter.register_rate_limiter())

        # Connecting to AI provider
        ai_service = self._create_ai_service()

        # Registering api routes
        self._configure_analysis_router(ai_service=ai_service)

    def _configure_authentication(self) -> None:
        """Registers authentication interceptor module"""
        logger.info("Registering authentication middleware")
        auth_middleware = AuthInterceptor(
            api_key_field_name=self.config.api_key_field_name,
            api_key=self.config.api_key
        ).register_auth_interceptor()
        self.app.add_middleware(auth_middleware)

    @staticmethod
    def _configure_rate_limiter() -> RateLimiter:
        # Getting env variables here as they aren't configurable by the user
        redis_host = os.environ.get("REDIS_HOST", "localhost")
        redis_port = int(os.environ.get("REDIS_PORT", 6379))
        rate_limiter = RateLimiter(host=redis_host, port=redis_port)
        return rate_limiter

    @asynccontextmanager
    async def _rate_limiting_redis_lifecycle(self, _app: FastAPI):
        """Registers redis lifecycle middleware"""
        task = asyncio.create_task(self.rate_limiter.flush_redis_periodically(interval_seconds=3600))
        yield
        # Shutdown: cancel the task
        task.cancel()

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
