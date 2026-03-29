"""API route definitions for the DataLens application."""

import datetime
import json
import langchain_core.exceptions
from fastapi import APIRouter, HTTPException

from src.ai.langchain.communication_service import AiCommunicationService
from src.model.api.api_model import BaseRequest, BaseResponse
from src.validation.validation import validate_request


class AnalysisRouter:  # pylint: disable=too-few-public-methods
    """Registers and handles all analysis API routes."""

    DATASET_SEPERATOR = "\n---NEW---DATASET---\n"

    def __init__(self, ai_service: AiCommunicationService):
        self.router = APIRouter()
        self.ai_service = ai_service
        self._register_routes()

    def _register_routes(self) -> None:
        """Registers all routes to the router."""
        self.router.add_api_route("/health", self._health, methods=["GET"])
        self.router.add_api_route("/forecasting", self._forecasting, methods=["POST"])
        self.router.add_api_route("/summary", self._summary, methods=["POST"])
        self.router.add_api_route("/anomaly", self._anomaly_detection, methods=["POST"])
        self.router.add_api_route("/pattern", self._pattern_recognition, methods=["POST"])
        self.router.add_api_route("/comparison", self._comparison, methods=["POST"])

    async def _health(self) -> dict:
        """Check the health of the service."""
        healthy = await self.ai_service.health_check()
        if healthy:
            return {"result": "healthy"}
        return {"result": "unhealthy"}

    async def _forecasting(self, request: BaseRequest) -> BaseResponse:
        """Perform time series forecasting."""
        return await self._do_analyze_request(request=request, analysis_type="forecasting")

    async def _summary(self, request: BaseRequest) -> BaseResponse:
        """Generate a summary of the data."""
        # Validating input data
        return await self._do_analyze_request(request=request, analysis_type="summary")

    async def _anomaly_detection(self, request: BaseRequest) -> BaseResponse:
        """Detect anomalies in the data."""
        return await self._do_analyze_request(request=request, analysis_type="anomaly")

    async def _pattern_recognition(self, request: BaseRequest) -> BaseResponse:
        """Recognize patterns in the data."""
        return await self._do_analyze_request(request=request, analysis_type="pattern")

    async def _comparison(self, request: BaseRequest) -> BaseResponse:
        """Compare datasets."""
        return await self._do_analyze_request(request=request, analysis_type="comparison")

    async def _do_analyze_request(self, request: BaseRequest, analysis_type: str) -> BaseResponse:
        """Base analyse request for ai."""
        # Validating input data
        message = validate_request(request=request)
        if not message == "":
            raise HTTPException(status_code=400, detail=f"Invalid request: {message}")

        # Preparing data and splitting list into string by separator
        prepared_data = self.DATASET_SEPERATOR.join(
            ds if isinstance(ds, str) else json.dumps(ds) for ds in request.data_sets
        )

        # Processing LLM-module call
        try:
            response = await self.ai_service.make_analyse_request(
                analysis_type=analysis_type,
                data=prepared_data,
                data_format=request.format,
                daterange=request.daterange
            )
        except langchain_core.exceptions.LangChainException as e:
            raise HTTPException(status_code=502, detail=f"Ollama request failed: {e}") from e
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid request: {e}") from e

        return BaseResponse(message=response, date=datetime.datetime.now().isoformat())
