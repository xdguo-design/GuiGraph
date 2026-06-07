"""AI 模型管理路由。"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response
from app.modules.ai.service import ai_model_service

router = APIRouter()


class ModelCreate(BaseModel):
    name: str
    provider: str = ""
    model_id: str = ""
    api_key: str = ""
    api_base: str = ""
    is_default: bool = False
    scenario: str = ""


class ModelUpdate(BaseModel):
    name: str | None = None
    provider: str | None = None
    model_id: str | None = None
    api_key: str | None = None
    api_base: str | None = None
    is_default: bool | None = None


@router.get("")
async def list_models(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await ai_model_service.list_models(db)
    return Response.ok({"items": items})


@router.post("")
async def create_model(
    body: ModelCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await ai_model_service.create_model(db, body.model_dump())
    return Response.ok(item)


@router.put("/{model_id}")
async def update_model(
    model_id: int,
    body: ModelUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await ai_model_service.update_model(db, model_id, body.model_dump(exclude_none=True))
    if not item:
        raise HTTPException(status_code=404, detail="模型不存在")
    return Response.ok(item)


@router.delete("/{model_id}")
async def delete_model(
    model_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ok = await ai_model_service.delete_model(db, model_id)
    if not ok:
        raise HTTPException(status_code=404, detail="模型不存在")
    return Response.ok({"message": "删除成功"})
