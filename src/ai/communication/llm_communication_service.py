"""LangChain communication module to chat with chosen model"""

import logging
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.exceptions import LangChainException
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langsmith import traceable

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


class CommunicationService:  # pylint: disable=too-few-public-methods
    """Provides for AI communication"""

    def __init__(self, provider: str, model: str, api_key: str):
        self.model = init_chat_model(model_provider=provider, model=model, api_key=api_key)

    async def health_check(self) -> bool:
        """Check the health of the service."""
        try:
            self.model.invoke(input="health_check")
        except LangChainException as e:
            logger.error("Health check failed: %s", e)
            return False
        # If operation does not fail -> Connection to LLM Provider is up and running
        return True

    @traceable(run_type="llm")
    async def make_analyse_request(
        self,
        analysis_type: str,
        data: str,
        data_format: str,
        daterange: list[str]
    ) -> str | list[Any]:
        """Makes a request to AI with system and user messages"""
        system_prompt = analyses_types.get(analysis_type)
        if system_prompt is None:
            raise ValueError(f"Unknown analysis type: '{analysis_type}'")

        # Adding format and time range to prompt
        system_prompt = system_prompt.format(
            data_format, f"{daterange[0]} to {daterange[1]}"
        )

        # Wrapping system and user data
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=data)]

        logger.info(f"Sending {analysis_type} analysis request to LLM")

        # Processing LLM call through selected provider
        try:
            response: AIMessage = await self.model.ainvoke(input=messages)
        except LangChainException as e:
            logger.error("LLM request failed: %s", e)
            raise LangChainException(e)

        return response.content
