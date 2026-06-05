"""Jenkins 集成模块 Schema 定义。"""

from typing import Optional

from pydantic import BaseModel, Field

from app.shared.enums import AuthType


class JenkinsInstanceCreate(BaseModel):
    """创建 Jenkins 实例。"""
    name: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., description="Jenkins URL")
    auth_type: AuthType = Field(AuthType.TOKEN, description="认证类型")
    auth_token: Optional[str] = Field(None, description="Token")


class JenkinsInstanceResponse(BaseModel):
    """Jenkins 实例响应。"""
    id: str
    name: str
    url: str
    auth_type: str
    created_by: str


class BuildRequest(BaseModel):
    """触发构建请求。"""
    job_name: str = Field(..., description="Job 全名")
    params: Optional[dict] = Field(None, description="构建参数")


class BuildStatusResponse(BaseModel):
    """构建状态响应。"""
    build_id: str
    job_name: str
    status: str = Field(..., description="状态: running/success/failed")
    message: str
    url: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class BuildLogResponse(BaseModel):
    """构建日志响应。"""
    build_id: str
    log: str = Field(..., description="构建日志内容")
