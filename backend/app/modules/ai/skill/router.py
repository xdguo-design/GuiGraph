"""AI Skill 管理路由。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response
from app.modules.ai.service import ai_skill_service

router = APIRouter()


@router.get("")
async def list_skills(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await ai_skill_service.list_skills(db)
    return Response.ok({"items": items})


@router.post("/{skill_id}/enable")
async def enable_skill(
    skill_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ok = await ai_skill_service.enable_skill(db, skill_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Skill 不存在")
    return Response.ok({"message": "启用成功"})


@router.post("/{skill_id}/disable")
async def disable_skill(
    skill_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ok = await ai_skill_service.disable_skill(db, skill_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Skill 不存在")
    return Response.ok({"message": "禁用成功"})
