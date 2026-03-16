"""Ollama communication module to chat with chosen model"""

import logging

import ollama
from ollama import ChatResponse

logger = logging.getLogger("logger")

BASE_ROLE = "You are a professional data analyst for analysing csv, json and yml files."

DATA_SEPERATOR = f"The key ---NEW---DATASET--- seperates different data sets."

analyses_types: dict[str, str] = {
    "forecasting":
        f"{BASE_ROLE}. "
        f"Provide for a forecasting for the following data. "
        f"This the format of the data: {{}}. "
        f"Analyse the format and continue the data in this format. "
        f"{DATA_SEPERATOR} "
        f"This the time range: {{}}. "
        f"Only return the existing data with forecasted data without a additional message",

    "summary":
        f"{BASE_ROLE}."
        f"Provide a summary for the following data. "
        f"This the format of the data: {{}}. "
        f"{DATA_SEPERATOR} "
        f"This the time range: {{}}. "
        f"Only return a human text comment. ",

    "anomaly":
        f"{BASE_ROLE}."
        f"Provide a anomaly detection for the following data. "
        f"This the format of the data: {{}}. "
        f"{DATA_SEPERATOR} "
        f"This the time range: {{}}. "
        f"Only return a human text comment. ",

    "pattern":
        f"{BASE_ROLE}."
        f"Detect patterns in the following data sets. "
        f"This the format of the data: {{}}. "
        f"{DATA_SEPERATOR} "
        f"This the time range: {{}}. "
        f"Only return a human text comment. ",

    "comparison":
        f"{BASE_ROLE}."
        f"Compare the following data sets"
        f"This the format of the data: {{}}. "
        f"{DATA_SEPERATOR} "
        f"This the time range: {{}}. "
        f"Only return a human text comment. ",
}


class OllamaService:  # pylint: disable=too-few-public-methods
    """Provides for ollama communication"""

    def __init__(self, ollama_base_url: str, ollama_model: str):
        self.ollama_model = ollama_model
        self.ollama_client = ollama.AsyncClient(host=ollama_base_url)

    async def health_check(self) -> bool:
        """Check the health of the service."""
        try:
            await self.ollama_client.list()
        except (ollama.ResponseError, ConnectionError) as e:
            logger.error("Ollama request failed: %s", e)
            return False
        # If operation does not fail -> ollama is up and running
        return True

    async def make_analyse_request(self, analysis_type: str, data: str, data_format: str, daterange: list[str]) -> str:
        """Makes a request to ollama with system and user messages"""
        system_prompt = analyses_types.get(analysis_type)
        if system_prompt is None:
            raise ValueError(f"Unknown analysis type: '{analysis_type}'")
        
        # Adding format and time range to prompt
        system_prompt = system_prompt.format(data_format, daterange)

        logger.info("Sending '%s' analysis request to Ollama", analysis_type)

        # Processing LLM call through Ollama
        try:
            response: ChatResponse = await self.ollama_client.chat(
                model=self.ollama_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": data},
                ],
            )
        except ollama.ResponseError as e:
            logger.error("Ollama request failed: %s", e)
            raise ollama.ResponseError(error=e.error, status_code=502)
        except ConnectionError as e:
            logger.error("Could not connect to Ollama: %s", e)
            raise ollama.ResponseError(error=str(e), status_code=502)

        return response.message.content
