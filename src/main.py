
from src.server.server import Server

app = Server().build().run()

if __name__ == "__main__":
    print("Hello from datalama!")
