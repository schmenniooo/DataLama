
from fastapi import FastAPI
from src.api.api import router

class Server:

    def __init__(self):
        app = FastAPI()

    def build(self):
        # Registering routes
        self.app.include_router(router)
        return self
    
    def run(self):
        return self.app

