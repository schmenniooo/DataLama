"""Entry point for the DataLama application."""

from src.server.server import Server
from dotenv import load_dotenv
import uvicorn
import os

def main():
    load_dotenv()  # No-op if .env doesn't exist (e.g. in Docker)
    debug = os.getenv("DEBUG", "false").lower() == "true"

    # Building app
    app = Server(
        api_key_field_name=os.getenv("API_KEY_FIELD_NAME"), 
        api_key=os.getenv("API_KEY")
    ).use_authenticaton().build().run()

    # Starting server
    uvicorn.run(
        app,
        debug=debug,
        reload=debug,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 3000))
    )

if __name__ == "__main__":
    print("Hello from datalama!")
    main()
