import asyncio
import random
import time

from aiohttp import ClientHandlerType, ClientRequest, ClientResponse


class RateLimitMiddleware:
    """
    Very simple per-host RPS limiter with jitter.
    """

    def __init__(
        self,
        default_rps: float,
        jitter_factor: float,
    ):
        self._default_rps = default_rps
        self._jitter_factor = jitter_factor

        self._lock: asyncio.Lock = asyncio.Lock()
        self._next_allowed_time: float = 0

    async def __call__(
        self,
        request: ClientRequest,
        handler: ClientHandlerType,
    ) -> ClientResponse:
        base_interval = 1.0 / self._default_rps

        if self._jitter_factor > 0:
            interval = base_interval * (1.0 + self._jitter_factor * random.random())
        else:
            interval = base_interval

        async with self._lock:
            now = time.monotonic()
            t = self._next_allowed_time

            slot = max(now, t)
            self._next_allowed_time = slot + interval

        sleep_duration = slot - now
        if sleep_duration > 0:
            await asyncio.sleep(sleep_duration)

        return await handler(request)