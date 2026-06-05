"""AI 能力模块 Schema 定义。"""

from pydantic import BaseModel


class AISearchResponse(BaseModel):
    """AI 搜索响应。"""
    results: list[dict]
    total: int
