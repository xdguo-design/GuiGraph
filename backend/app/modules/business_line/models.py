"""业务线模块 ORM 模型。"""

from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base, TimestampMixin


class BusinessLine(Base, TimestampMixin):
    """业务线表。"""
    __tablename__ = "business_line"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="业务线名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="业务线编码")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="描述")
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="负责人 ID")
    status: Mapped[str] = mapped_column(String(20), default="active", comment="状态: active/inactive")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "owner_id": str(self.owner_id) if self.owner_id else None,
            "status": self.status,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
