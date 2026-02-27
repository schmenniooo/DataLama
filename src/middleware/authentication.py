"""Authentication module"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class AuthInterceptor:
    """Handles authentication through api tokens"""

    def __init__(self, api_key_field_name: str, api_key: str):
        self.api_key_field_name = api_key_field_name 
        self.api_key = api_key

    def register_auth_interceptor(self):
        api_key_field_name = self.api_key_field_name
        api_key = self.api_key

        class _Middleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next):
                # Validating env keys
                if not api_key_field_name or not api_key:
                    return JSONResponse({"detail": "Unauthorized"}, status_code=401)

                # Extracting response token
                token = request.headers.get(api_key_field_name)
                if token != api_key:
                    return JSONResponse({"detail": "Unauthorized"}, status_code=401)
                return await call_next(request)
        return _Middleware
