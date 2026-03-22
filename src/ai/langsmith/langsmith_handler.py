"""Module to handle tracing with LangSmith"""

from langsmith import Client

class LangSmithHandler:

    def __init__(self, api_key: str, project_name: str):
        self.client = Client(api_key=api_key)

    def check_langsmith_connection(self) -> bool:
        pass
