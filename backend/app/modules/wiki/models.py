"""Wiki 结构化文档模块 ORM 模型。"""

from sqlalchemy import String, Integer, Text, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, TimestampMixin


class WikiSpace(Base, TimestampMixin):
    """Wiki 空间表。"""
    __tablename__ = "wiki_space"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="空间名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="空间编码")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="空间描述")
    owner_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="所属团队/部门 ID")
    owner_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="所有者类型: team/department")
    read_roles: Mapped[list[str]] = mapped_column(JSON, nullable=False, comment="可读角色列表")
    write_roles: Mapped[list[str]] = mapped_column(JSON, nullable=False, comment="可写角色列表")

    docs = relationship("WikiDoc", back_populates="space", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "owner_id": str(self.owner_id),
            "owner_type": self.owner_type,
        }


class WikiDoc(Base, TimestampMixin):
    """Wiki 文档表。"""
    __tablename__ = "wiki_doc"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    space_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="所属空间 ID")
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="文档标题")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="文档内容（Markdown）")
    parent_doc_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="父文档 ID（嵌套目录）")
    order_num: Mapped[int] = mapped_column(Integer, default=0, comment="排序序号")
    depth: Mapped[int] = mapped_column(Integer, default=0, comment="嵌套深度（0-4）")
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default_factory=list, comment="标签列表")
    related_change_ids: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, comment="关联变更 ID 数组")
    related_func_point_ids: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, comment="关联功能点 ID 数组")
    author_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="作者 ID")
    is_published: Mapped[bool] = mapped_column(default=False, comment="是否发布")
    view_count: Mapped[int] = mapped_column(Integer, default=0, comment="阅读量")
    edit_count: Mapped[int] = mapped_column(Integer, default=0, comment="编辑量")

    space = relationship("WikiSpace", back_populates="docs")
    parent_doc = relationship("WikiDoc", remote_side=[id], backref="child_docs")
    versions = relationship("WikiDocVersion", back_populates="doc", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "space_id": str(self.space_id),
            "title": self.title,
            "content": self.content,
            "parent_doc_id": str(self.parent_doc_id) if self.parent_doc_id else None,
            "order_num": self.order_num,
            "depth": self.depth,
            "tags": self.tags,
            "related_change_ids": self.related_change_ids,
            "author_id": str(self.author_id),
            "is_published": self.is_published,
            "view_count": self.view_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class WikiDocVersion(Base, TimestampMixin):
    """Wiki 文档版本历史表。"""
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
        }
