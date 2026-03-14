"""Ollama communication module to chat with chosen model"""

import logging

from fastapi import HTTPException
import ollama
from ollama import ChatResponse

logger = logging.getLogger("logger")

base_role = ("You are a professional data analyst for analysing csv, json and yml files. "
             "First check which file format was chosen")

data_seperator = f"The key ---NEW---DATASET--- seperates different data sets."

analyses_types: dict[str, str] = {
    "forecasting": f"{base_role}. "
                   f"Provide for a forecasting for the following data. "
                   f"Analyse the format and continue the data in this format. "
                   f"{data_seperator}"
                   f"Only return the existing data with forecasted data without a additional message",
    "summary": f"{base_role}.",
    "anomaly": f"{base_role}.",
    "pattern": f"{base_role}.",
    "comparison": f"{base_role}.",
}


class OllamaService:  # pylint: disable=too-few-public-methods
    """Provides for ollama communication"""

    def __init__(self, ollama_base_url: str, ollama_model: str):
        self.ollama_model = ollama_model
        self.ollama_client = ollama.AsyncClient(host=ollama_base_url)

    async def health_check(self) -> bool:
        """Check the health of the service."""
        try:
            self.ollama_client.list()
        except ollama.ResponseError as e:
            logger.error("Ollama request failed: %s", e)
            return False
        # If operation does not fail -> ollama is up and running
        return True

    async def make_analyse_request(self, analysis_type: str, data: str) -> str:
        """Makes a request to ollama with system and user messages"""
        system_prompt = analyses_types.get(analysis_type)
        if system_prompt is None:
            raise ValueError(f"Unknown analysis type: '{analysis_type}'")

        logger.info("Sending '%s' analysis request to Ollama", analysis_type)
        try:
            response: ChatResponse = self.ollama_client.chat(
                model=self.ollama_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": data},
                ],
            )
        except ollama.ResponseError as e:
            logger.error("Ollama request failed: %s", e)
            raise ollama.ResponseError(error=e.error, status_code=502)

        return response.message.content
