"""Ollama communication module to chat with chosen model"""

import ollama

analyses_types: dict[str, str] = {
    "forecasting" : "",
    "summary" : "",
    "anomaly" : "",
    "pattern" : "",
    "comparison" : "",
}

class OllamaService:
    """Provides for ollama communication"""
    
    def __init__(self, ollama_base_url: str, ollama_model: str):
        self.ollama_model = ollama_model
        self.ollama_client = ollama.Client(host=ollama_base_url)
        
    def make_analyse_request(self, analysis_type: str, data: str) -> bool:
        """Makes a request to ollama with system and user messages"""
        # Getting system prompt by given analysis type
        system_prompt = analyses_types.get(analysis_type)
        if system_prompt is None:
            raise ValueError(f"Unknown analysis type: '{analysis_type}'")

        # Making chat request
        try:
            self.ollama_client.chat(
                model=self.ollama_model,
                messages=[
                    {"role": "system", "content": system_prompt}, # Configuring model
                    {"role": "user", "content": data}, # Analysing actual data
                ],
            )
        except ollama.ResponseError:
            return False

        return True
