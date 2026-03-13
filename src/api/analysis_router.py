"""API route definitions for the DataLama application."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

from src.ollama.ollama_service import OllamaService

class BaseRequest(BaseModel):
    data: str

class BaseResponse(BaseModel):
    message: str
    updated_data: str

class AnalysisRouter:  # pylint: disable=too-few-public-methods
    """Registers and handles all analysis API routes."""

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
        healthy = self.ollama_service.health_check()
        if healthy:
            return {"result": "healthy"}
        else:
            return {"result": "unhealthy"}

    async def _forecasting(self, request: BaseRequest) -> BaseResponse:
        """Perform time series forecasting."""
        response = self.ollama_service.make_analyse_request(
            analysis_type="forecasting",
            data=request.data,
        )
        return BaseResponse(message=response, updated_data=request.data) # TODO: Data updated by LLM

    async def _summary(self) -> None:
        """Generate a summary of the data."""

    async def _anomaly_detection(self) -> None:
        """Detect anomalies in the data."""

    async def _pattern_recognition(self) -> None:
        """Recognize patterns in the data."""

    async def _comparison(self) -> None:
        """Compare datasets."""
