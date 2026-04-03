"""Authentication module"""

import logging
from typing import Callable, Type

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

logger = logging.getLogger("logger")


class AuthInterceptor:  # pylint: disable=too-few-public-methods
    """Handles authentication through api tokens"""

    def __init__(self, api_key_field_name: str, api_key: str):
        self.api_key_field_name = api_key_field_name
        self.api_key = api_key

    def register_auth_interceptor(self) -> Type[BaseHTTPMiddleware]:
        """Returns inner base middleware class for auth middleware. Compares api key from request header"""
        api_key_field_name = self.api_key_field_name
        api_key = self.api_key

        class _Middleware(BaseHTTPMiddleware):  # pylint: disable=too-few-public-methods
            async def dispatch(self, request: Request, call_next: Callable) -> Response:
                # Validating env keys
                if not api_key_field_name or not api_key:
                    logger.error("API key configuration is missing")
                    return JSONResponse({"detail": "Unauthorized"}, status_code=401)

                token = request.headers.get(api_key_field_name)
                if token != api_key:
                    logger.warning("Rejected request with invalid API key")
                    return JSONResponse({"detail": "Unauthorized"}, status_code=401)
                return await call_next(request)
        return _Middleware
