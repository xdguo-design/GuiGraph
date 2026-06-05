"""AI 能力模块路由。"""

from fastapi import APIRouter

from app.core.utils.response import Response

router = APIRouter()


@router.get("/rag/search")
async def rag_search(query: str):
    """RAG 语义搜索。"""
    return Response.ok({"results": []})


@router.post("/rag/analyze")
async def rag_analyze(document: str):
    """文档分析。"""
    return Response.ok({"analysis": "分析结果"})


@router.post("/generate/summary")
async def generate_summary(content: str):
    """生成总结。"""
    return Response.ok({"summary": "总结内容"})
