"""变更管理模块 Schema 定义。"""

from typing import Optional

from pydantic import BaseModel, Field

from app.shared.enums import ChangeType, ChangeReason, ChangeStatus


class ChangeItemCreate(BaseModel):
    """创建变更请求。"""
    version_id: str = Field(..., description="所属版本 ID")
    change_type: ChangeType = Field(..., description="变更类型")
    content: str = Field(..., min_length=10, description="变更内容描述")
    effect_scope: Optional[str] = Field(None, description="影响范围")
    change_reason: ChangeReason = Field(..., description="变更原因")
    change_reason_detail: Optional[str] = Field(None, description="变更原因补充")
    related_requirement_no: Optional[str] = Field(None, description="关联需求号")
    func_point_ids: Optional[list[str]] = Field(None, description="关联功能点 ID 数组")
    img_list: Optional[list[str]] = Field(None, description="图片 URL 数组")
    file_ref: Optional[list[str]] = Field(None, description="文档引用数组")
    team_id: Optional[int] = Field(None, description="所属团队 ID")


class ChangeItemUpdate(BaseModel):
    """更新变更请求。"""
    content: Optional[str] = None
    effect_scope: Optional[str] = None
    change_reason_detail: Optional[str] = None
    related_requirement_no: Optional[str] = None
    func_point_ids: Optional[list[str]] = None
    img_list: Optional[list[str]] = None
    file_ref: Optional[list[str]] = None
    team_id: Optional[int] = None
    change_reason: Optional[ChangeReason] = None


class ChangeItemResponse(BaseModel):
    """变更响应。"""
    id: str
    version_id: str
    change_type: str
    content: str
    effect_scope: Optional[str] = None
    change_reason: str
    change_reason_detail: Optional[str] = None
    related_requirement_no: Optional[str] = None
    func_point_ids: Optional[list[str]] = None
    img_list: Optional[list[str]] = None
    file_ref: Optional[list[str]] = None
    impact_tables: Optional[list[str]] = None
    impact_apis: Optional[list[str]] = None
    related_incidents: Optional[list[str]] = None
    rag_doc_id: Optional[str] = None
    status: str
    created_by: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ChangeListResponse(BaseModel):
    """变更列表响应。"""
    items: list[ChangeItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ChangeApproveRequest(BaseModel):
    """审批变更请求。"""
    approved: bool = Field(..., description="是否通过")
    comment: Optional[str] = Field(None, description="审批意见")
