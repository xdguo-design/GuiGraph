"""认证模块 Schema 定义。"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求。"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名/邮箱/手机")
    password: str = Field(..., min_length=1, description="密码")
    remember_me: bool = Field(False, description="记住登录")


class TokenResponse(BaseModel):
    """令牌响应。"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(7200, description="过期时间（秒）")


class WechatQRCodeResponse(BaseModel):
    """微信二维码响应。"""
    qr_url: str = Field(..., description="微信扫码 URL")
