"""请求日志中间件（记录所有 API 请求）。"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from loguru import logger


class RequestLogMiddleware(BaseHTTPMiddleware):
    """记录所有 API 请求的中间件。"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()

        # 记录请求
        logger.info(
            f"[{request.method}] {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        response = await call_next(request)

        # 计算耗时
        process_time = time.perf_counter() - start_time

        # 记录响应
        logger.info(
            f"[{request.method}] {request.url.path} "
            f"status={response.status_code} "
            f"time={process_time:.3f}s"
        )

        # 添加响应头
        response.headers["X-Process-Time"] = str(process_time)

        return response
