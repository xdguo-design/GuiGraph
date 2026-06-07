"""审计日志路由。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response, PageResponse
from app.modules.audit.service import audit_service

router = APIRouter()


@router.get("")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Query(""),
    operation: str = Query(""),
    start_time: str = Query(""),
    end_time: str = Query(""),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询审计日志。"""
    items, total = await audit_service.list_logs(
        db, page=page, page_size=page_size,
        user_id=user_id, operation=operation,
        start_time=start_time, end_time=end_time,
    )
    return Response.ok(PageResponse.paginate(items=items, total=total, page=page, page_size=page_size))
