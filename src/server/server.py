"""Server module for building and running the FastAPI application."""
import logging
import os

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from src.ai.langchain.communication_service import AiCommunicationService
from src.ai.knowledge.knowledge_base_service import KnowledgeBaseService
from src.api.analysis_router import AnalysisRouter
from src.middleware.authentication import AuthInterceptor
from src.middleware.rate_limiter import RateLimiter
from src.model.config import Config

logger = logging.getLogger("logger")


class Server:  # pylint: disable=too-few-public-methods
    """Builds and configures the FastAPI application."""

    def __init__(self, config: Config):
        logger.info("Configuring datalens server")
        self.config = config

        # Creating FastAPI instance
        self.app = FastAPI()

        # Skipping authentication in debug mode
        if not config.debug:
            self._configure_authentication()

        # Create rate limiter
        self._configure_rate_limiter()

        # Connecting to AI provider
        ai_service = self._create_ai_service()

        # Registering auto knowledge-base handler if enabled
        if config.knowledge_base_enabled:
            self._configure_knowledge_base_service()

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

    def _configure_rate_limiter(self) -> RateLimiter:
        logger.info("Registering rate limiter")
        # Getting env variables here as they aren't configurable by the user
        redis_host = os.environ.get("REDIS_HOST", "localhost")
        redis_port = int(os.environ.get("REDIS_PORT", 6379))
        rate_limiter = RateLimiter(host=redis_host, port=redis_port)

        # Registering rate limiter middleware
        self.app.add_middleware(rate_limiter.register_rate_limiter())
        return rate_limiter

    def _create_ai_service(self) -> AiCommunicationService:
        """Returns new AI service class"""
        logger.info(f"Creating AI communication service with {self.config.model}")
        return AiCommunicationService(
            provider=self.config.llm_provider,
            model=self.config.model,
            api_key=self.config.llm_provider_api_token,
        )

    def _configure_knowledge_base_service(self) -> None:
        # Check for existence of config file
        if self.config.knowledge_base_config_path is None:
            logger.info("No knowledge base config path provided")
            return

        # Injecting config file path to new service
        service = KnowledgeBaseService(config_file_path=self.config.knowledge_base_config_path)

        # Registering scheduler to auto update knowledge base
        scheduler = AsyncIOScheduler()
        scheduler.add_job(service.knowledge_base_fetch_workflow, "interval", minutes=30)
        return

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
