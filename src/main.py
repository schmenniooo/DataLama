"""Entry point for the DataLama application."""

import os
import logging

from dotenv import load_dotenv

from src.server.server import Server
from src.model.config import Config

logger = logging.getLogger("logger")

def main():
    """Starts the DataLama application."""
    load_dotenv()  # No-op if .env doesn't exist (e.g. in Docker)

    # Configuring app
    config = Config(
        api_key_field_name = os.getenv("API_KEY_FIELD_NAME"),
        api_key = os.getenv("API_KEY"),
        debug = os.getenv("DEBUG", "false").lower() == "true",
        host = os.getenv("HOST", "0.0.0.0"),
        port = int(os.getenv("PORT", "3000")),
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", ""),
        ollama_model = os.getenv("OLLAMA_MODEL", "")
    )

    # Creating and running server
    server = Server(config=config)
    server.run()

if __name__ == "__main__":
    print("Hello from datalama!")
    main()
