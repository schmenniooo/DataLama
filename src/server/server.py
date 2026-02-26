"""Server module for building and running the FastAPI application."""

from fastapi import FastAPI
from src.api.api import router


class Server:
    """Builds and configures the FastAPI application."""

    def __init__(self):
        self.app = FastAPI()

    def build(self):
        """Register routes and return the server instance."""
        self.app.include_router(router)
        return self

    def run(self):
        """Return the configured FastAPI application."""
        return self.app
