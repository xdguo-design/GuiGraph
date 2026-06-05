"""审计日志路由。"""

from fastapi import APIRouter, Depends

from app.core.deps.auth import get_current_user
from app.core.utils.response import Response, PageResponse

router = APIRouter()


@router.get("")
async def list_audit_logs(
    page: int = 1,
    page_size: int = 20,
    user_id: str = "",
    operation: str = "",
    start_time: str = "",
    end_time: str = "",
    current_user: str = Depends(get_current_user),
):
    """查询审计日志。"""
    return Response.ok(PageResponse.paginate(items=[], total=0, page=page, page_size=page_size))
