"""升级日志路由。"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response, PageResponse
from app.modules.upgrade.models import SysUpgradeLog

router = APIRouter()


@router.get("")
async def list_upgrade_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    version: str = Query(""),
    status: str = Query(""),
    start_time: str = Query(""),
    end_time: str = Query(""),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询升级日志。"""
    conditions = []
    if version:
        conditions.append(
            SysUpgradeLog.version_from.contains(version) |
            SysUpgradeLog.version_to.contains(version)
        )
    if status:
        conditions.append(SysUpgradeLog.status == status)

    where = and_(*conditions) if conditions else True
    total = (await db.execute(select(func.count(SysUpgradeLog.id)).where(where))).scalar() or 0
    q = (
        select(SysUpgradeLog)
        .where(where)
        .order_by(SysUpgradeLog.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = (await db.execute(q)).scalars().all()
    items = [r.to_dict() for r in rows]
    return PageResponse.paginate(items=items, total=total, page=page, page_size=page_size)


@router.get("/{log_id}")
async def get_upgrade_detail(
    log_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取升级详情。"""
    row = await db.get(SysUpgradeLog, log_id)
    if not row:
        return JSONResponse(
            status_code=404,
            content=Response.fail(message="未找到", code="NOT_FOUND"),
        )
    return Response.ok(row.to_dict())


@router.post("/{log_id}/rollback")
async def rollback_upgrade(
    log_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """执行回滚。"""
    row = await db.get(SysUpgradeLog, log_id)
    if not row:
        return JSONResponse(
            status_code=404,
            content=Response.fail(message="未找到", code="NOT_FOUND"),
        )
    row.status = "rolled_back"
    return Response.ok({"message": "回滚成功"})


@router.post("/{log_id}/export")
async def export_upgrade_log(
    log_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """导出升级日志。"""
    row = await db.get(SysUpgradeLog, log_id)
    if not row:
        return JSONResponse(
            status_code=404,
            content=Response.fail(message="未找到", code="NOT_FOUND"),
        )
    return Response.ok({"message": "导出成功", "data": row.to_dict()})
