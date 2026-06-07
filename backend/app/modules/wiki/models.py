"""Wiki 模块 ORM 模型。"""

from sqlalchemy import String, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, TimestampMixin


class WikiSpace(Base, TimestampMixin):
    """Wiki 空间表。"""
    __tablename__ = "wiki_space"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="空间名称")
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="空间标识")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="描述")
    owner_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="所有者 ID")
    visibility: Mapped[str] = mapped_column(String(20), default="team", comment="可见性: public/team/private")
    read_roles: Mapped[list[str]] = mapped_column(JSON, default_factory=list, comment="可读角色")
    write_roles: Mapped[list[str]] = mapped_column(JSON, default_factory=list, comment="可写角色")

    docs = relationship("WikiDoc", back_populates="space", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "key": self.key,
            "description": self.description,
            "owner_id": str(self.owner_id),
            "visibility": self.visibility,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class WikiDoc(Base, TimestampMixin):
    """Wiki 文档表。"""
    __tablename__ = "wiki_doc"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    space_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="空间 ID")
    parent_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="父文档 ID")
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="标题")
    content: Mapped[str] = mapped_column(Text, default="", comment="内容（Markdown）")
    author_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="作者 ID")
    tags: Mapped[list[str]] = mapped_column(JSON, default_factory=list, comment="标签")
    order_num: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    is_published: Mapped[bool] = mapped_column(default=False, comment="是否发布")

    space = relationship("WikiSpace", back_populates="docs")
    versions = relationship("WikiDocVersion", back_populates="doc", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "space_id": str(self.space_id),
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "title": self.title,
            "content": self.content,
            "author_id": str(self.author_id),
            "tags": self.tags,
            "order_num": self.order_num,
            "is_published": self.is_published,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class WikiDocVersion(Base, TimestampMixin):
    """Wiki 文档版本表。"""
    __tablename__ = "wiki_doc_version"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doc_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="文档 ID")
    version_num: Mapped[int] = mapped_column(Integer, nullable=False, comment="版本号")
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="标题")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="内容")
    change_desc: Mapped[str | None] = mapped_column(Text, nullable=True, comment="变更说明")
    author_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="修改人 ID")

    doc = relationship("WikiDoc", back_populates="versions")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "doc_id": str(self.doc_id),
            "version_num": self.version_num,
            "title": self.title,
            "content": self.content,
            "change_desc": self.change_desc,
            "author_id": str(self.author_id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
