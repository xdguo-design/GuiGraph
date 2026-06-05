"""AI Skill 管理路由。"""

from fastapi import APIRouter

from app.core.utils.response import Response

router = APIRouter()


@router.get("")
async def list_skills():
    """列出 Skill。"""
    return Response.ok({"items": []})


@router.post("/{skill_id}/enable")
async def enable_skill(skill_id: str):
    """启用 Skill。"""
    return Response.ok({"message": "启用成功"})


@router.post("/{skill_id}/disable")
async def disable_skill(skill_id: str):
    """禁用 Skill。"""
    return Response.ok({"message": "禁用成功"})
