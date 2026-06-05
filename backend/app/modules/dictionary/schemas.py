"""字典管理 Schema 定义。"""

from pydantic import BaseModel, Field


class DomainResponse(BaseModel):
    """领域响应。"""
    id: str
    name: str
    code: str


class ApplicationResponse(BaseModel):
    """应用响应。"""
    id: str
    name: str
    code: str


class ComponentResponse(BaseModel):
    """组件响应。"""
    id: str
    name: str
    code: str
