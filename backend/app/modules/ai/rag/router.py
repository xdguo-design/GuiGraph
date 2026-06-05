"""RAG 检索路由。"""

from fastapi import APIRouter

from app.core.utils.response import Response

router = APIRouter()


@router.post("/search")
async def rag_search(query: str):
    """RAG 语义搜索。"""
    return Response.ok({"results": []})


@router.post("/analyze")
async def rag_analyze(document: str):
    """文档分析。"""
    return Response.ok({"analysis": "分析结果"})
