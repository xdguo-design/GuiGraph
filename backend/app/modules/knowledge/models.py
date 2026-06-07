"""知识库笔记模块 ORM 模型。"""

from sqlalchemy import String, Integer, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, TimestampMixin


class KnowledgeBase(Base, TimestampMixin):
    """知识库表。"""
    __tablename__ = "knowledge_base"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="知识库名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="知识库编码")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="知识库描述")
    owner_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="所属团队/部门 ID")
    owner_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="所有者类型: team/department")
    read_roles: Mapped[list[str]] = mapped_column(JSON, nullable=False, comment="可读角色列表")
    write_roles: Mapped[list[str]] = mapped_column(JSON, nullable=False, comment="可写角色列表")

    notes = relationship("Note", back_populates="knowledge_base", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "owner_id": str(self.owner_id),
            "owner_type": self.owner_type,
        }


class Note(Base, TimestampMixin):
    """笔记表。"""
    __tablename__ = "note"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    knowledge_base_id: Mapped[int] = mapped_column(Integer, ForeignKey("knowledge_base.id", ondelete="CASCADE"), nullable=False, comment="所属知识库 ID")
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="笔记标题")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="笔记内容（Markdown）")
    parent_note_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("note.id", ondelete="CASCADE"), nullable=True, comment="父笔记 ID（嵌套目录）")
    order_num: Mapped[int] = mapped_column(Integer, default=0, comment="排序序号")
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list, comment="标签列表")
    related_change_ids: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, comment="关联变更 ID 数组")
    related_func_point_ids: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, comment="关联功能点 ID 数组")
    author_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="作者 ID")
    is_published: Mapped[bool] = mapped_column(default=False, comment="是否发布")

    knowledge_base = relationship("KnowledgeBase", back_populates="notes")
    parent_note = relationship("Note", remote_side=[id], backref="child_notes")
    versions = relationship("NoteVersion", back_populates="note", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "knowledge_base_id": str(self.knowledge_base_id),
            "title": self.title,
            "content": self.content,
            "parent_note_id": str(self.parent_note_id) if self.parent_note_id else None,
            "order_num": self.order_num,
            "tags": self.tags,
            "related_change_ids": self.related_change_ids,
            "author_id": str(self.author_id),
            "is_published": self.is_published,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class NoteVersion(Base, TimestampMixin):
    """笔记版本历史表。"""
    __tablename__ = "note_version"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey("note.id", ondelete="CASCADE"), nullable=False, comment="笔记 ID")
    version_num: Mapped[int] = mapped_column(Integer, nullable=False, comment="版本号")
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="标题")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="内容")
    change_desc: Mapped[str | None] = mapped_column(Text, nullable=True, comment="变更说明")
    author_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="修改人 ID")

    note = relationship("Note", back_populates="versions")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "note_id": str(self.note_id),
            "version_num": self.version_num,
            "title": self.title,
            "content": self.content,
            "change_desc": self.change_desc,
            "author_id": str(self.author_id),
        }
