"""Entry point for the DataLens application."""

import os
import logging

from dotenv import load_dotenv

from src.server.server import Server
from src.model.config.config import Config

logger = logging.getLogger("logger")

def main():
    """Starts the DataLens application."""
    load_dotenv()  # No-op if .env doesn't exist (e.g. in Docker)

    # Configuring app
    config = Config(
        api_key_field_name = os.getenv("API_KEY_FIELD_NAME", ""),
        api_key = os.getenv("API_KEY", ""),
        llm_provider=os.getenv("LLM_PROVIDER", ""),
        llm_provider_api_token = os.getenv("LLM_PROVIDER_API_TOKEN", ""),
        model = os.getenv("MODEL", ""),
        knowledge_base_enabled=os.getenv("KNOWLEDGE_BASE_ENABLED", "false").lower() == "true",
        knowledge_base_config_path=os.getenv("KNOWLEDGE_BASE_CONFIG_PATH", ""),
        langsmith_tracing_enabled=os.getenv("LANGSMITH_TRACING_ENABLED", "false").lower() == "true",
        langsmith_api_key = os.getenv("LANGSMITH_API_KEY", ""),
        langsmith_project = os.getenv("LANGSMITH_PROJECT", ""),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "3000")),
    )

    # Creating and running server
    server = Server(config=config)
    server.run()

if __name__ == "__main__":
    print("Hello from DataLens!")
    main()
