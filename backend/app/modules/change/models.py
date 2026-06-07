"""变更管理模块 ORM 模型。"""

import json

from sqlalchemy import String, Integer, DateTime, Text, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base, TimestampMixin
from app.shared.enums import ChangeType, ChangeReason, ChangeStatus


class BizChangeItem(Base, TimestampMixin):
    """变更明细表。"""
    __tablename__ = "biz_change_item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="所属版本 ID")
    change_type: Mapped[ChangeType] = mapped_column(Enum(ChangeType), nullable=False, comment="变更类型")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="变更内容描述")
    effect_scope: Mapped[str | None] = mapped_column(Text, nullable=True, comment="影响范围描述")
    change_reason: Mapped[ChangeReason] = mapped_column(Enum(ChangeReason), nullable=False, comment="变更原因")
    change_reason_detail: Mapped[str | None] = mapped_column(Text, nullable=True, comment="变更原因补充")
    related_requirement_no: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="关联需求号")
    func_point_ids: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, comment="关联功能点 ID 数组")
    img_list: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, comment="MinIO 图片签名地址数组")
    file_ref: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, comment="关联文档/PDF 地址数组")
    impact_tables: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, comment="GraphRAG 推断的影响表")
    impact_apis: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, comment="GraphRAG 推断的影响接口")
    related_incidents: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, comment="关联的历史故障 ID 数组")
    rag_doc_id: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="关联 RAG 知识库 ID")
    git_repo_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="关联 Git 仓库 ID")
    git_branch_source: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="源分支")
    git_branch_target: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="目标分支")
    git_merge_commit: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="合并 Commit Hash")
    jenkins_build_id: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="关联 Jenkins 构建 ID")
    status: Mapped[ChangeStatus] = mapped_column(Enum(ChangeStatus), default=ChangeStatus.DRAFT, comment="变更状态")
    team_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="所属团队 ID（看板按团队着色）")
    created_by: Mapped[int] = mapped_column(Integer, nullable=False, comment="创建人 ID")
    approved_by: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="审批人 ID")
    approved_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True, comment="审批时间")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "version_id": str(self.version_id),
            "change_type": self.change_type.value,
            "content": self.content,
            "effect_scope": self.effect_scope,
            "change_reason": self.change_reason.value,
            "change_reason_detail": self.change_reason_detail,
            "related_requirement_no": self.related_requirement_no,
            "func_point_ids": self.func_point_ids,
            "img_list": self.img_list,
            "file_ref": self.file_ref,
            "impact_tables": self.impact_tables,
            "impact_apis": self.impact_apis,
            "related_incidents": self.related_incidents,
            "rag_doc_id": self.rag_doc_id,
            "status": self.status.value,
            "team_id": str(self.team_id) if self.team_id else None,
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
