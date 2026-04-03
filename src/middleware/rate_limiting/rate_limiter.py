"""Module for handling rate limiting with Redis"""

from typing import Type, Callable
import asyncio

from redis.asyncio import (Redis, RedisError)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse


class RateLimiter:

    MAX_REQUESTS_PER_SECOND = 10

    BURST_SIZE = 20

    def __init__(self, host: str = "localhost", port: int = 6379):
        self.redis = Redis(host=host, port=port, db=0, decode_responses=True)

    async def flush_redis_periodically(self, interval_seconds: int):
        await asyncio.sleep(interval_seconds)
        await self.redis.flushdb()

    def register_rate_limiter(self) -> Type[BaseHTTPMiddleware]:
        redis = self.redis
        class _Middleware(BaseHTTPMiddleware): # pylint: disable=too-few-public-methods
            async def dispatch(self, request: Request, call_next: Callable) -> Response:
                try:
                    if request.client is not None:
                        return await call_next(request)
                    ip = request.client.host

                    request_counter = int(await redis.get(ip))
                    if request_counter is None:
                        return JSONResponse({"detail": "Unauthorized"}, status_code=401)

                    if request_counter >= RateLimiter.MAX_REQUESTS_PER_SECOND:
                        return Response(status_code=429)

                    # Happens in every case
                    await redis.set(ip, request_counter + 1)
                except RedisError:
                    raise RedisError("Redis Error")
                return await call_next(request)
        return _Middleware
