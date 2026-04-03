"""Module for handling rate limiting with Redis"""

from typing import Type, Callable

from redis.asyncio import (Redis, RedisError)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RateLimiter:

    TIME_WINDOW = 60
    MAX_REQUESTS_PER_MINUTE = 10

    def __init__(self, host: str = "localhost", port: int = 6379):
        self.redis = Redis(host=host, port=port, db=0, decode_responses=True)

    def register_rate_limiter(self) -> Type[BaseHTTPMiddleware]:
        redis = self.redis
        class _Middleware(BaseHTTPMiddleware): # pylint: disable=too-few-public-methods
            async def dispatch(self, request: Request, call_next: Callable) -> Response:
                try:
                    if request.client is None:
                        return await call_next(request)

                    # Fetching requests counter for ip
                    ip = request.client.host
                    request_counter = await redis.get(name=ip)

                    if request_counter is None:
                        # client ip not registered yet -> letting trough
                        await redis.set(name=ip, value=0, ex=RateLimiter.TIME_WINDOW)
                        return await call_next(request)

                    # Converting to Integer
                    request_counter = int(request_counter)
                    if request_counter >= RateLimiter.MAX_REQUESTS_PER_MINUTE:
                        # client overflowed the limit
                        await redis.set(name=ip, value=request_counter + 1, ex=RateLimiter.TIME_WINDOW)
                        return Response(status_code=429)

                    # Increasing counter in every case
                    await redis.set(name=ip, value=request_counter + 1, ex=RateLimiter.TIME_WINDOW)
                except RedisError:
                    raise RedisError("Redis Error")
                return await call_next(request)
        return _Middleware
