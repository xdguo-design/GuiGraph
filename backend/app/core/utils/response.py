"""统一响应格式。"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class Response(BaseModel):
    """统一 API 响应模型。"""

    code: str = Field(default="OK", description="响应码")
    message: str = Field(default="success", description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")

    @classmethod
    def ok(cls, data: Any = None, message: str = "success") -> dict:
        """成功响应。"""
        return {"code": "OK", "message": message, "data": data}

    @classmethod
    def fail(cls, message: str = "error", code: str = "ERROR", data: Any = None) -> dict:
        """失败响应。"""
        return {"code": code, "message": message, "data": data}


class PageResponse(BaseModel):
    """分页响应模型。"""

    code: str = "OK"
    message: str = "success"
    data: dict = Field(description="分页数据")

    @classmethod
    def paginate(
        cls,
        items: list,
        total: int,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """分页响应。"""
        return {
            "code": "OK",
            "message": "success",
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
            },
        }
