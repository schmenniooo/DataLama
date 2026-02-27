"""Entry point for the DataLama application."""

from src.server.server import Server

app = Server().use_authenticaton().build().run()

if __name__ == "__main__":
    print("Hello from datalama!")
