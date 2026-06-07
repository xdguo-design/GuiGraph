"""变更管理模块路由。"""

from fastapi import APIRouter, Depends

from app.core.deps.auth import get_current_user
from app.core.utils.response import Response
from app.modules.change.schemas import (
    ChangeItemCreate, ChangeItemResponse, ChangeItemUpdate,
    ChangeApproveRequest,
)

router = APIRouter()


@router.get("")
async def list_changes(
    page: int = 1,
    page_size: int = 20,
    change_type: str = "",
    status: str = "",
    team_id: str = "",
    user_id: str = Depends(get_current_user),
):
    """查询变更列表。"""
    # TODO: 从数据库查询
    total_pages = (0 + page_size - 1) // page_size if page_size > 0 else 0
    return Response.ok({
        "items": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    })


@router.get("/{change_id}")
async def get_change(change_id: str, user_id: str = Depends(get_current_user)):
    """获取变更详情。"""
    return Response.ok(ChangeItemResponse(
        id=change_id,
        version_id="v001",
        change_type="db",
        content="示例变更内容",
        change_reason="requirement",
        status="draft",
        created_by=user_id,
    ))


@router.post("")
async def create_change(
    body: ChangeItemCreate,
    user_id: str = Depends(get_current_user),
):
    """创建变更申请。"""
    return Response.ok(ChangeItemResponse(
        id="chg_001",
        version_id=body.version_id,
        change_type=body.change_type,
        content=body.content,
        change_reason=body.change_reason,
        status="draft",
        created_by=user_id,
    ))


@router.put("/{change_id}")
async def update_change(
    change_id: str,
    body: ChangeItemUpdate,
    user_id: str = Depends(get_current_user),
):
    """更新变更。"""
    return Response.ok({"message": "更新成功"})


@router.post("/{change_id}/approve")
async def approve_change(
    change_id: str,
    body: ChangeApproveRequest,
    user_id: str = Depends(get_current_user),
):
    """审批变更。"""
    return Response.ok({"message": "审批成功"})
