"""SQLAlchemy 声明性基类。"""

from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """所有 ORM 模型的基类。"""
    pass


class TimestampMixin:
    """时间戳混入类（所有模型自动包含 created_at / updated_at）。"""
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="更新时间",
    )
