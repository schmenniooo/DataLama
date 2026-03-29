"""Module for handling rate limiting with Redis"""

from typing import Type

from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter:

    def __init__(self):
        pass

    def register_rate_limiter(self) -> Type[BaseHTTPMiddleware]:
        class _Middleware(BaseHTTPMiddleware): # pylint: disable=too-few-public-methods
            pass
        return _Middleware
