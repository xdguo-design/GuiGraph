"""用户模块 Schema 定义。"""

from typing import Optional

from pydantic import BaseModel, Field, EmailStr


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


class UserProfileUpdate(BaseModel):
    """更新用户资料请求（所有字段可选）。"""
    nickname: Optional[str] = Field(None, description="昵称")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")


class BindWechatRequest(BaseModel):
    """绑定微信请求。"""
    code: str = Field(..., min_length=4, description="微信授权 code（dev 模式下任意 4 位以上字符串）")


class BindWechatResponse(BaseModel):
    """绑定微信响应。"""
    openid: str = Field(..., description="微信 OpenID")
    nickname: str = Field("", description="微信昵称")
    message: str = Field("绑定成功", description="提示信息")
    mode: str = Field("mock", description="real=真实模式, mock=开发模式")


class WechatQrCodeResponse(BaseModel):
    """微信二维码响应。"""
    qr_url: str = Field("", description="二维码 URL（dev 模式为空）")
    mode: str = Field("dev", description="real=真实模式, dev=开发模式")
    tip: str = Field("", description="前端提示")


# ── 注册申请相关 ──

class ApplicationSubmit(BaseModel):
    """注册申请提交（公开）。"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=4, max_length=50, description="密码")
    nickname: Optional[str] = Field(None, max_length=100, description="昵称")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    reason: Optional[str] = Field(None, max_length=500, description="申请原因")


class ApplicationReview(BaseModel):
    """管理员审核申请。"""
    role: str = Field(..., description="分配的角色")
    company_id: Optional[str] = Field(None, description="分配的公司 ID")
    department_id: Optional[str] = Field(None, description="分配的部门 ID")
    team_id: Optional[str] = Field(None, description="分配的团队 ID")
    comment: Optional[str] = Field(None, max_length=500, description="审核意见")


class ApplicationReject(BaseModel):
    """管理员拒绝申请。"""
    comment: Optional[str] = Field(None, max_length=500, description="拒绝原因")
