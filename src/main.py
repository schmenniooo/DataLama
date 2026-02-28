"""Entry point for the DataLama application."""

import os

from dotenv import load_dotenv

from src.server.server import Server


def main():
    """Starts the DataLama application."""
    load_dotenv()  # No-op if .env doesn't exist (e.g. in Docker)

    api_key_field_name = os.getenv("API_KEY_FIELD_NAME")
    api_key = os.getenv("API_KEY")

    debug = os.getenv("DEBUG", "false").lower() == "true"
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "3000"))

    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "")
    ollama_model = os.getenv("OLLAMA_MODEL", "")

    # Creating the app server
    server = Server(
        api_key_field_name=api_key_field_name,
        api_key=api_key
    )

    # Running the app server
    server.use_authenticaton().setup_ai_model(
        ollama_base_url=ollama_base_url, 
        ollama_model=ollama_model
    ).build().run(
        debug=debug,
        host=host,
        port=port
    )

if __name__ == "__main__":
    print("Hello from datalama!")
    main()
