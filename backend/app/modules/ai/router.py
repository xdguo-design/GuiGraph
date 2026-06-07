"""AI 能力模块路由。"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response
from app.modules.ai.service import ai_service

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class AnalyzeRequest(BaseModel):
    document: str


class SummaryRequest(BaseModel):
    content: str


@router.post("/rag/search")
async def rag_search(
    body: SearchRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """RAG 语义搜索。"""
    if not body.query or not body.query.strip():
        return JSONResponse(
            status_code=422,
            content=Response.fail(message="查询内容不能为空", code="VALIDATION_ERROR"),
        )
    results = await ai_service.rag_search(db, body.query, body.top_k)
    return Response.ok({"results": results})


@router.post("/rag/analyze")
async def rag_analyze(
    body: AnalyzeRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """文档分析。"""
    result = await ai_service.rag_analyze(db, body.document)
    return Response.ok(result)


@router.post("/generate/summary")
async def generate_summary(
    body: SummaryRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """生成总结。"""
    result = await ai_service.generate_summary(db, body.content)
    return Response.ok(result)
