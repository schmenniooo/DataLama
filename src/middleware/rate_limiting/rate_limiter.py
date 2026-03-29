"""Module for handling rate limiting with Redis"""

from typing import Type, Callable

from redis import Redis, RedisError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RateLimiter:

    def __init__(self, host: str = "localhost", port: int = 6379):
        self.redis = Redis(host=host, port=port, db=0, decode_responses=True)

    def register_rate_limiter(self) -> Type[BaseHTTPMiddleware]:
        redis = self.redis
        class _Middleware(BaseHTTPMiddleware): # pylint: disable=too-few-public-methods
            async def dispatch(self, request: Request, call_next: Callable) -> Response:
                try:
                    await redis.set("Key", "Value")
                except RedisError:
                    raise RedisError("Redis Error")
                return await call_next(request)
        return _Middleware
