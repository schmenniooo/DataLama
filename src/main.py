"""Entry point for the DataLama application."""

from src.server.server import Server
from dotenv import load_dotenv
import os

def main():
    load_dotenv()  # No issue if .env doesn't exist (e.g. in Docker)

    api_key_field_name = os.getenv("API_KEY_FIELD_NAME")
    api_key = os.getenv("API_KEY")

    debug = os.getenv("DEBUG", "false").lower() == "true"
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 3000))

    # Building app
    Server(
        api_key_field_name=api_key_field_name, 
        api_key=api_key
    ).use_authenticaton().build().run(
        debug=debug,
        host=host,
        port=port
    )

if __name__ == "__main__":
    print("Hello from datalama!")
    main()
