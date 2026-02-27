"""Entry point for the DataLama application."""

from src.server.server import Server
import uvicorn
import os

def main():
    app = Server().use_authenticaton().build().run()
    uvicorn.run(
        app, 
        host=os.getenv("HOST", "127.0.0.1"), 
        port=os.getenv("PORT", 3000)
    )

if __name__ == "__main__":
    print("Hello from datalama!")
    main()
