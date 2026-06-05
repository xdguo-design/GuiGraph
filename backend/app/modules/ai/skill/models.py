"""Skill 管理模块 ORM 模型。"""

from sqlalchemy import String, Integer, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base, TimestampMixin


class AiSkill(Base, TimestampMixin):
    """AI Skill 配置表。"""
    __tablename__ = "ai_skill"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, comment="Skill 名称")
    description: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="Skill 描述")
    skill_file: Mapped[str] = mapped_column(String(200), nullable=False, comment="Skill 文件路径")
    version: Mapped[str] = mapped_column(String(20), nullable=False, comment="版本号")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    allowed_roles: Mapped[list[str]] = mapped_column(JSON, nullable=False, comment="允许的角色列表")
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="Skill 配置")
    created_by: Mapped[int] = mapped_column(Integer, nullable=False, comment="创建人 ID")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "skill_file": self.skill_file,
            "version": self.version,
            "enabled": self.enabled,
            "allowed_roles": self.allowed_roles,
            "config": self.config,
            "created_by": str(self.created_by),
        }
