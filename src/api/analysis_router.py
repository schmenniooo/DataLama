"""API route definitions for the DataLama application."""

from fastapi import APIRouter, HTTPException, Request
import ollama

from src.ollama.ollama_service import OllamaService
from src.validation.validation import validate_request
from src.model.api.api_model import BaseRequest, BaseResponse

class AnalysisRouter:  # pylint: disable=too-few-public-methods
    """Registers and handles all analysis API routes."""

    DATASET_SEPERATOR = "\n---NEW---DATASET---\n"

    def __init__(self, ollama_service: OllamaService):
        self.router = APIRouter()
        self.ollama_service = ollama_service
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
        healthy = await self.ollama_service.health_check()
        if healthy:
            return {"result": "healthy"}
        else:
            return {"result": "unhealthy"}

    async def _forecasting(self, request: BaseRequest) -> BaseResponse:
        """Perform time series forecasting."""

        # Validating input data
        message = validate_request(request=request)
        if not message == "":
            raise HTTPException(status_code=400, detail=f"Invalid request: {message}")

        # Processing LLM-module call
        try:
            response = await self.ollama_service.make_analyse_request(
                analysis_type="forecasting",
                data=self.DATASET_SEPERATOR.join(request.data_sets),
            )
        except ollama.ResponseError as e:
            raise HTTPException(status_code=502, detail=f"Ollama request failed: {e.error}")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid request: {e}")
        
        return BaseResponse(message="Forecasted Data", updated_data=response.split(self.DATASET_SEPERATOR))

    async def _summary(self) -> None:
        """Generate a summary of the data."""

    async def _anomaly_detection(self) -> None:
        """Detect anomalies in the data."""

    async def _pattern_recognition(self) -> None:
        """Recognize patterns in the data."""

    async def _comparison(self) -> None:
        """Compare datasets."""
