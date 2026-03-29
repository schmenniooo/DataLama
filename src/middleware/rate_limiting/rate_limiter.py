"""Module for handling rate limiting with Redis"""

from typing import Type

from redis import Redis
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter:

    def __init__(self, host: str = "localhost", port: int = 6379):
        self.redis = Redis(host=host, port=port, db=0, decode_responses=True)

    def register_rate_limiter(self) -> Type[BaseHTTPMiddleware]:
        class _Middleware(BaseHTTPMiddleware): # pylint: disable=too-few-public-methods
            self.redis.set("key", "value")
        return _Middleware
