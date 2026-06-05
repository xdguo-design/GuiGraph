"""知识库笔记路由。"""

from fastapi import APIRouter, Depends

from app.core.deps.auth import get_current_user
from app.core.utils.response import Response

router = APIRouter()


@router.get("")
async def list_notes(user_id: str = Depends(get_current_user)):
    """列出笔记。"""
    return Response.ok({"items": []})


@router.get("/{note_id}")
async def get_note(note_id: str, user_id: str = Depends(get_current_user)):
    """获取笔记详情。"""
    return Response.ok({"message": "详情"})


@router.post("")
async def create_note(user_id: str = Depends(get_current_user)):
    """创建笔记。"""
    return Response.ok({"message": "创建成功"})


@router.put("/{note_id}")
async def update_note(note_id: str, user_id: str = Depends(get_current_user)):
    """更新笔记。"""
    return Response.ok({"message": "更新成功"})


@router.delete("/{note_id}")
async def delete_note(note_id: str, user_id: str = Depends(get_current_user)):
    """删除笔记。"""
    return Response.ok({"message": "删除成功"})


@router.post("/{note_id}/ai-generate")
async def ai_generate_note(note_id: str, user_id: str = Depends(get_current_user)):
    """AI 生成笔记草稿。"""
    return Response.ok({"message": "生成成功"})
