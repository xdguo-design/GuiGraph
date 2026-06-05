"""字典管理模块 ORM 模型。"""

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, TimestampMixin


class BizDomain(Base, TimestampMixin):
    """领域字典表。"""
    __tablename__ = "biz_domain"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="领域名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="领域编码")
    team_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="所属团队 ID")

    team = relationship("BizTeam", back_populates="domains")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "code": self.code,
            "team_id": str(self.team_id),
        }


class BizApplication(Base, TimestampMixin):
    """应用字典表。"""
    __tablename__ = "biz_application"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="应用名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="应用编码")
    team_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="所属团队 ID")

    team = relationship("BizTeam", back_populates="applications")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "code": self.code,
            "team_id": str(self.team_id),
        }


class BizComponent(Base, TimestampMixin):
    """组件字典表。"""
    __tablename__ = "biz_component"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="组件名称")
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="组件编码")
    team_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="所属团队 ID")

    team = relationship("BizTeam", back_populates="components")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "code": self.code,
            "team_id": str(self.team_id),
        }
