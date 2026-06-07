"""业务线路由。"""

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response
from app.modules.business_line.service import business_line_service

router = APIRouter()


# ── Schemas ──

class BusinessLineCreate(BaseModel):
    name: str
    code: str
    description: str = ""
    owner_id: int = 0
    status: str = "active"
    sort_order: int = 0


class BusinessLineUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    description: str | None = None
    owner_id: int | None = None
    status: str | None = None
    sort_order: int | None = None


# ── 路由 ──

@router.get("")
async def list_business_lines(
    status: str = Query(""),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询业务线列表。"""
    items = await business_line_service.list_lines(db, status=status)
    return Response.ok({"items": items})


@router.get("/{line_id}")
async def get_business_line(
    line_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取业务线详情。"""
    item = await business_line_service.get_line(db, line_id)
    if not item:
        raise HTTPException(status_code=404, detail="业务线不存在")
    return Response.ok(item)


@router.post("")
async def create_business_line(
    body: BusinessLineCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建业务线。"""
    item = await business_line_service.create_line(db, body.model_dump())
    return Response.ok(item)


@router.put("/{line_id}")
async def update_business_line(
    line_id: int,
    body: BusinessLineUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新业务线。"""
    data = body.model_dump(exclude_none=True)
    item = await business_line_service.update_line(db, line_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="业务线不存在")
    return Response.ok(item)


@router.delete("/{line_id}")
async def delete_business_line(
    line_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除业务线。"""
    ok = await business_line_service.delete_line(db, line_id)
    if not ok:
        raise HTTPException(status_code=404, detail="业务线不存在")
    return Response.ok({"message": "删除成功"})
