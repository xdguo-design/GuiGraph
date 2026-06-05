"""AI 模型管理路由。"""

from fastapi import APIRouter

from app.core.utils.response import Response

router = APIRouter()


@router.get("")
async def list_models():
    """列出 AI 模型。"""
    return Response.ok({"items": []})


@router.post("")
async def create_model():
    """添加 AI 模型。"""
    return Response.ok({"message": "添加成功"})


@router.put("/{model_id}")
async def update_model(model_id: str):
    """更新 AI 模型。"""
    return Response.ok({"message": "更新成功"})


@router.delete("/{model_id}")
async def delete_model(model_id: str):
    """删除 AI 模型。"""
    return Response.ok({"message": "删除成功"})
