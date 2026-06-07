"""Git 集成模块 ORM 模型。"""

from datetime import datetime
from sqlalchemy import String, Integer, Text, Enum, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, TimestampMixin
from app.shared.enums import AuthType


class BizGitRepo(Base, TimestampMixin):
    """Git 仓库表。"""
    __tablename__ = "biz_git_repo"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("biz_team.id"), nullable=False, comment="所属团队 ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="仓库名称")
    url: Mapped[str] = mapped_column(String(500), nullable=False, comment="Git 仓库地址")
    auth_type: Mapped[AuthType] = mapped_column(Enum(AuthType), nullable=False, comment="认证类型")
    auth_token: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="Token（加密存储）")
    ssh_key: Mapped[str | None] = mapped_column(Text, nullable=True, comment="SSH 私钥（加密存储）")
    default_branch: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="默认分支")
    protected_branches: Mapped[list[str] | None] = mapped_column(Text, nullable=True, comment="受保护分支列表（JSON）")
    created_by: Mapped[int] = mapped_column(Integer, nullable=False, comment="创建人 ID")

    user_auths = relationship("BizUserGitAuth", back_populates="repo", cascade="all, delete-orphan")
    jenkins_jobs = relationship("BizJenkinsJob", back_populates="repo", cascade="all, delete-orphan")
    change_items = relationship("BizChangeItem", back_populates="git_repo", foreign_keys="BizChangeItem.git_repo_id")

    def to_dict(self) -> dict:
        import json
        return {
            "id": str(self.id),
            "team_id": str(self.team_id),
            "name": self.name,
            "url": self.url,
            "auth_type": self.auth_type.value if hasattr(self.auth_type, "value") else self.auth_type,
            "default_branch": self.default_branch,
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "protected_branches": json.loads(self.protected_branches) if self.protected_branches else [],
        }


class BizUserGitAuth(Base, TimestampMixin):
    """用户-Git 授权表。"""
    __tablename__ = "biz_user_git_auth"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="用户 ID")
    repo_id: Mapped[int] = mapped_column(Integer, ForeignKey("biz_git_repo.id"), nullable=False, comment="Git 仓库 ID")
    granted_by: Mapped[int] = mapped_column(Integer, nullable=False, comment="授权人 ID")
    granted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="授权时间")

    repo = relationship("BizGitRepo", back_populates="user_auths")

    __table_args__ = (
        UniqueConstraint("user_id", "repo_id", name="uk_user_repo"),
    )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "repo_id": str(self.repo_id),
            "granted_by": str(self.granted_by),
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
        }
