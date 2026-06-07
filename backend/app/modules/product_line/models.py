"""产品线模块 ORM 模型。"""

from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, TimestampMixin


class ProductLine(Base, TimestampMixin):
    """产品线表。"""
    __tablename__ = "product_line"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    business_line_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("business_line.id"), nullable=False, comment="所属业务线 ID"
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="产品线名称")
    code: Mapped[str] = mapped_column(String(50), nullable=False, comment="产品线编码")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="描述")
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="负责人 ID")
    status: Mapped[str] = mapped_column(String(20), default="active", comment="状态: active/inactive")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "business_line_id": str(self.business_line_id),
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "owner_id": str(self.owner_id) if self.owner_id else None,
            "status": self.status,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
