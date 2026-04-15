"""Server module for building and running the FastAPI application."""
import logging
import os

from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from ai.knowledge.knowledge_base_service import KnowledgeBaseService
from src.ai.communication.llm_communication_service import CommunicationService
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

        # Creating FastAPI instance with lifespan
        self.app = FastAPI(lifespan=self._lifespan)

        # Skipping authentication in debug mode
        if not config.debug:
            self._configure_authentication()

        # Create rate limiter
        self._configure_rate_limiter()

        # Preparing knowledge-base scheduler if enabled
        self.kb_scheduler = None
        self.retriever = None
        if config.knowledge_base_enabled:
            service = self._configure_knowledge_base_service()
            if service:
                # Getting chroma vector store as retriever
                self.retriever = service.get_chroma_retriever()

        # Connecting to AI provider
        ai_service = self._create_ai_service()

        # Registering api routes
        self._configure_analysis_router(ai_service=ai_service)

    @asynccontextmanager
    async def _lifespan(self, _app: FastAPI):
        # Startup: start the knowledge base scheduler if configured
        if self.kb_scheduler:
            logger.info("Starting knowledge base scheduler")
            self.kb_scheduler.start()
        yield
        # Shutdown: stop the scheduler
        if self.kb_scheduler:
            self.kb_scheduler.shutdown()

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

    def _create_ai_service(self) -> CommunicationService:
        """Returns new AI service class"""
        logger.info(f"Creating AI communication service with {self.config.model}")
        return CommunicationService(
            provider=self.config.llm_provider,
            model=self.config.model,
            api_key=self.config.llm_provider_api_token,
            chroma_retriever=self.retriever
        )

    def _configure_knowledge_base_service(self) -> KnowledgeBaseService | None:
        # Check for existence of config file
        if self.config.knowledge_base_config_path is None:
            logger.info("No knowledge base config path provided")
            return None

        # Injecting config file path to new service
        service = KnowledgeBaseService(config_file_path=self.config.knowledge_base_config_path)

        # Registering scheduler to auto update knowledge base (started in lifespan)
        self.kb_scheduler = AsyncIOScheduler()
        # TODO: Replace 1 minute interval
        self.kb_scheduler.add_job(service.knowledge_base_fetch_workflow, "interval", minutes=1)
        return service

    def _configure_analysis_router(self, ai_service: CommunicationService) -> None:
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
