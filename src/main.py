
from src.server.server import Server

def main():
    print("Hello from datalama!")
    newServer = Server().build()
    return newServer.run()

if __name__ == "__main__":
    main()
