"""全局异常处理器。"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from loguru import logger

from app.core.utils.response import Response


def register_exception_handlers(app: FastAPI) -> None:
    """注册所有全局异常处理。"""

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"全局异常: {exc}")
        return JSONResponse(
            status_code=500,
            content=Response.fail("服务器内部错误", code="INTERNAL_ERROR"),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning(f"参数校验失败: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content=Response.fail(
                "参数校验失败",
                code="VALIDATION_ERROR",
                data={"errors": exc.errors()},
            ),
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content=Response.fail("资源不存在", code="NOT_FOUND"),
        )

    @app.exception_handler(401)
    async def unauthorized_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content=Response.fail("未授权访问", code="UNAUTHORIZED"),
        )

    @app.exception_handler(403)
    async def forbidden_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content=Response.fail("禁止访问", code="FORBIDDEN"),
        )
