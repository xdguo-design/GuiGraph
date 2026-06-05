"""用户模块 ORM 模型。"""

from datetime import datetime

from sqlalchemy import String, Enum, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base, TimestampMixin
from app.shared.enums import LoginMethod, UserStatus


class SysUser(Base, TimestampMixin):
    """系统用户表。"""
    __tablename__ = "sys_user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    nickname: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="昵称")
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="头像 URL")
    email: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True, comment="邮箱")
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="手机号")
    wechat_openid: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True, comment="微信 OpenID")
    wechat_unionid: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="微信 UnionID")
    password_hash: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="密码 MD5")
    login_method: Mapped[LoginMethod] = mapped_column(
        Enum(LoginMethod), default=LoginMethod.PASSWORD, comment="登录方式"
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus), default=UserStatus.ACTIVE, comment="用户状态"
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="最后登录时间")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "username": self.username,
            "nickname": self.nickname,
            "avatar_url": self.avatar_url,
            "email": self.email,
            "phone": self.phone,
            "status": self.status.value,
            "login_method": self.login_method.value,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }
