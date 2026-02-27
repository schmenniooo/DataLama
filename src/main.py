"""Entry point for the DataLama application."""

from src.server.server import Server
import uvicorn
import os

def main():
    # Building app
    app = Server(
        api_key_field_name=os.getenv("API_KEY_FIELD_NAME"), 
        api_key=os.getenv("API_KEY")
    ).use_authenticaton().build().run()

    # Starting server
    uvicorn.run(
        app, 
        host=os.getenv("HOST", "0.0.0.0"), 
        port=int(os.getenv("PORT", 3000))
    )

if __name__ == "__main__":
    print("Hello from datalama!")
    main()
