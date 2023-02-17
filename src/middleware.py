import time

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


class TimerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
            self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response