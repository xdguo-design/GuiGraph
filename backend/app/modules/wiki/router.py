"""Wiki 结构化文档路由。"""

from fastapi import APIRouter, Depends

from app.core.deps.auth import get_current_user
from app.core.utils.response import Response

router = APIRouter()


@router.get("/spaces")
async def list_spaces(user_id: str = Depends(get_current_user)):
    """列出 Wiki 空间。"""
    return Response.ok({"items": []})


@router.get("/docs")
async def list_docs(user_id: str = Depends(get_current_user)):
    """列出文档。"""
    return Response.ok({"items": []})


@router.get("/{doc_id}")
async def get_doc(doc_id: str, user_id: str = Depends(get_current_user)):
    """获取文档详情。"""
    return Response.ok({"message": "详情"})


@router.post("/docs")
async def create_doc(user_id: str = Depends(get_current_user)):
    """创建文档。"""
    return Response.ok({"message": "创建成功"})


@router.put("/docs/{doc_id}")
async def update_doc(doc_id: str, user_id: str = Depends(get_current_user)):
    """更新文档。"""
    return Response.ok({"message": "更新成功"})


@router.delete("/docs/{doc_id}")
async def delete_doc(doc_id: str, user_id: str = Depends(get_current_user)):
    """删除文档。"""
    return Response.ok({"message": "删除成功"})
