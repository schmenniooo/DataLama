"""Module for handling rate limiting with Redis"""

from typing import Type, Callable
import asyncio

from redis.asyncio import (Redis, RedisError)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse


class RateLimiter:

    MAX_REQUESTS_PER_SECOND = 10

    def __init__(self, host: str = "localhost", port: int = 6379):
        self.redis = Redis(host=host, port=port, db=0, decode_responses=True)

    async def flush_redis_periodically(self, interval_seconds: int):
        while True:
            await asyncio.sleep(interval_seconds)
            await self.redis.flushdb()

    def register_rate_limiter(self) -> Type[BaseHTTPMiddleware]:
        redis = self.redis
        class _Middleware(BaseHTTPMiddleware): # pylint: disable=too-few-public-methods
            async def dispatch(self, request: Request, call_next: Callable) -> Response:
                try:
                    if request.client is None:
                        return await call_next(request)

                    # Fetching requests counter for ip
                    ip = request.client.host
                    request_counter = await redis.get(ip)

                    if request_counter is None:
                        # client ip not registered yet -> letting trough
                        return await call_next(request)

                    # Converting to Integer
                    request_counter = int(request_counter)
                    if request_counter >= RateLimiter.MAX_REQUESTS_PER_SECOND:
                        # client overflowed the limit
                        await redis.set(ip, request_counter + 1)
                        return Response(status_code=429)

                    # Increasing counter in every case
                    await redis.set(ip, request_counter + 1)
                except RedisError:
                    raise RedisError("Redis Error")
                return await call_next(request)
        return _Middleware
