"""Ollama communication module to chat with chosen model"""

import logging

import ollama

logger = logging.getLogger("logger")

analyses_types: dict[str, str] = {
    "forecasting": "",
    "summary": "",
    "anomaly": "",
    "pattern": "",
    "comparison": "",
}


class OllamaService:  # pylint: disable=too-few-public-methods
    """Provides for ollama communication"""

    def __init__(self, ollama_base_url: str, ollama_model: str):
        self.ollama_model = ollama_model
        self.ollama_client = ollama.Client(host=ollama_base_url)

    def make_analyse_request(self, analysis_type: str, data: str) -> bool:
        """Makes a request to ollama with system and user messages"""
        system_prompt = analyses_types.get(analysis_type)
        if system_prompt is None:
            raise ValueError(f"Unknown analysis type: '{analysis_type}'")

        logger.info("Sending '%s' analysis request to Ollama", analysis_type)
        try:
            self.ollama_client.chat(
                model=self.ollama_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": data},
                ],
            )
        except ollama.ResponseError as e:
            logger.error("Ollama request failed: %s", e)
            return False

        return True
