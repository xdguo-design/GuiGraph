"""升级日志路由。"""

from fastapi import APIRouter, Depends

from app.core.deps.auth import get_current_user
from app.core.utils.response import Response, PageResponse

router = APIRouter()


@router.get("")
async def list_upgrade_logs(
    page: int = 1,
    page_size: int = 20,
    version: str = "",
    status: str = "",
    start_time: str = "",
    end_time: str = "",
    current_user: str = Depends(get_current_user),
):
    """查询升级日志。"""
    return Response.ok(PageResponse.paginate(items=[], total=0, page=page, page_size=page_size))


@router.get("/{log_id}")
async def get_upgrade_detail(log_id: str, current_user: str = Depends(get_current_user)):
    """获取升级详情。"""
    return Response.ok({"message": "详情"})


@router.post("/{log_id}/rollback")
async def rollback_upgrade(log_id: str, current_user: str = Depends(get_current_user)):
    """执行回滚。"""
    return Response.ok({"message": "回滚成功"})


@router.post("/{log_id}/export")
async def export_upgrade_log(log_id: str, current_user: str = Depends(get_current_user)):
    """导出升级日志。"""
    return Response.ok({"message": "导出成功"})
