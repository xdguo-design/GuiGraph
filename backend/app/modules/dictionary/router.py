"""字典管理路由。"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response

router = APIRouter()


class DictItemCreate(BaseModel):
    name: str
    code: str
    parent_id: int | None = None
    description: str = ""


# ── 业务线/产品线/组件 ──

@router.get("/domains")
async def list_domains(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取领域/业务线列表。"""
    return Response.ok({"items": []})


@router.post("/domains")
async def create_domain(body: DictItemCreate, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """创建领域/业务线。"""
    return Response.ok({"message": "创建成功", "name": body.name})


@router.get("/applications")
async def list_applications(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取应用/产品线列表。"""
    return Response.ok({"items": []})


@router.post("/applications")
async def create_application(body: DictItemCreate, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """创建应用/产品线。"""
    return Response.ok({"message": "创建成功", "name": body.name})


@router.get("/components")
async def list_components(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取组件列表。"""
    return Response.ok({"items": []})


@router.post("/components")
async def create_component(body: DictItemCreate, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """创建组件。"""
    return Response.ok({"message": "创建成功", "name": body.name})
