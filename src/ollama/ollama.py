
import ollama

analyses_types: dict[str, str] = {
    "forecasting" : "",
    "summary" : "",
    "anomaly" : "",
    "pattern" : "",
    "comparison" : "",
}

class OllamaService:
    
    def __init__(self, ollama_base_url: str, ollama_model: str):
        self.base_url = ollama_base_url
        self.model = ollama_model

    def connect():
        pass

    def disconnect():
        pass
