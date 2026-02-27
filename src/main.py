"""Entry point for the DataLama application."""

from src.server.server import Server

def main():
    app = Server().use_authenticaton().build().run()
    return app

if __name__ == "__main__":
    print("Hello from datalama!")
    main()
