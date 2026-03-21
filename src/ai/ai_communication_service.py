"""Ollama communication module to chat with chosen model"""

import logging

from langchain_core.exceptions import LangChainException

import ai
from langchain.chat_models import init_chat_model

logger = logging.getLogger("logger")

BASE_ROLE = "You are a professional data analyst for analysing csv, json and yml files."

DATA_SEPERATOR = "Separate each dataset with exactly: ---NEW---DATASET---."

BASE_PROMPT = (
        BASE_ROLE + " "
        "{}"
        "{}"
        + DATA_SEPERATOR + " "
        "This the format of the data: {{}}. "
        "Analyse the format and continue the data in this format. "
        "This the time range: {{}}. "
)

analyses_types: dict[str, str] = {
    "forecasting":
        BASE_PROMPT.format(
            "Provide for a forecasting for the following data "
            "and continue the data in this format. ",
            "Return ONLY the raw data in the original format "
            "with calculated forecasting. "
            "No explanations, no headers, no markdown. "
        ),

    "summary":
        BASE_PROMPT.format(
            "Provide a summary for the following data. ",
            "Only return a human text comment. "
        ),

    "anomaly":
        BASE_PROMPT.format(
            "Provide a anomaly detection for the following data. ",
            "Only return a human text comment. "
        ),

    "pattern":
        BASE_PROMPT.format(
            "Detect patterns in the following data sets. ",
            "Only return a human text comment. "
        ),

    "comparison":
        BASE_PROMPT.format(
            "Compare the following data sets. ",
            "Only return a human text comment. "
        ),
}


class AiCommunicationService:  # pylint: disable=too-few-public-methods
    """Provides for ai communication"""

    def __init__(self, model: str):
        self.model = init_chat_model(model)

    async def health_check(self) -> bool:
        """Check the health of the service."""
        try:
            self.model.invoke("health_check")
        except LangChainException as e:
            logger.error("Health check failed: %s", e)
            return False
        # If operation does not fail -> Connection to LLM Provider is up and running
        return True

    async def make_analyse_request(
        self,
        analysis_type: str,
        data: str,
        data_format: str,
        daterange: list[str]
    ) -> str:
        """Makes a request to ai with system and user messages"""
        system_prompt = analyses_types.get(analysis_type)
        if system_prompt is None:
            raise ValueError(f"Unknown analysis type: '{analysis_type}'")

        # Adding format and time range to prompt
        system_prompt = system_prompt.format(
            data_format, f"{daterange[0]} to {daterange[1]}"
        )

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
        except ai.ResponseError as e:
            logger.error("Ollama request failed: %s", e)
            raise ai.ResponseError(error=e.error, status_code=502)
        except ConnectionError as e:
            logger.error("Could not connect to Ollama: %s", e)
            raise ai.ResponseError(error=str(e), status_code=502)

        return response.message.content
