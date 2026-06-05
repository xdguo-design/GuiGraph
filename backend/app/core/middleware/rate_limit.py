"""速率限制中间件（基础实现，生产环境建议用 Redis）。"""

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.utils.response import Response as APIResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """基于 IP 的速率限制中间件（内存版）。"""

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        ip = request.client.host if request.client else "unknown"
        now = time.time()

        # 清理过期记录
        self.requests[ip] = [
            t for t in self.requests[ip]
            if now - t < self.window_seconds
        ]

        # 检查限制
        if len(self.requests[ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content=APIResponse.fail("请求过于频繁，请稍后重试", code="RATE_LIMIT"),
            )

        self.requests[ip].append(now)
        return await call_next(request)
