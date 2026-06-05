"""用户模块 Schema 定义。"""

from typing import Optional

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """用户资料。"""
    id: str = Field(..., description="用户 ID")
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar_url: Optional[str] = Field(None, description="头像 URL")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    status: str = Field("active", description="状态")
    roles: list[str] = Field(default_factory=list, description="角色列表")


class AvatarUploadResponse(BaseModel):
    """头像上传响应。"""
    avatar_url: str = Field(..., description="头像 URL")
    message: str = Field(..., description="响应消息")


class BindWechatRequest(BaseModel):
    """绑定微信请求。"""
    code: str = Field(..., description="微信授权 code")
