"""用户模块 ORM 模型。"""

from datetime import datetime

from sqlalchemy import String, Enum, DateTime, Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base, TimestampMixin
from app.shared.enums import LoginMethod, UserStatus, ApplicationStatus


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


class SysUserApplication(Base, TimestampMixin):
    """注册申请表（用户注册需经管理员审核通过）。"""
    __tablename__ = "sys_user_application"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    password_hash: Mapped[str] = mapped_column(String(32), nullable=False, comment="密码 MD5")
    nickname: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="昵称")
    email: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="邮箱")
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="手机号")
    reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="申请原因")
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.PENDING, comment="申请状态"
    )
    # 审核信息
    reviewed_by: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="审核人 user_id")
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="审核时间")
    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True, comment="审核意见")
    # 审核通过后分配的信息（持久化在申请单上，便于追溯）
    assigned_role: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="分配的角色")
    assigned_company_id: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="分配的公司")
    assigned_department_id: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="分配的部门")
    assigned_team_id: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="分配的团队")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "username": self.username,
            "nickname": self.nickname,
            "email": self.email,
            "phone": self.phone,
            "reason": self.reason,
            "status": self.status.value,
            "reviewed_by": str(self.reviewed_by) if self.reviewed_by is not None else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "review_comment": self.review_comment,
            "assigned_role": self.assigned_role,
            "assigned_company_id": self.assigned_company_id,
            "assigned_department_id": self.assigned_department_id,
            "assigned_team_id": self.assigned_team_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
