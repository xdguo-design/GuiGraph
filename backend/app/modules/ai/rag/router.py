"""RAG 检索路由。"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response
from app.modules.ai.service import ai_service

router = APIRouter()


class SearchBody(BaseModel):
    query: str
    top_k: int = 5


class AnalyzeBody(BaseModel):
    document: str


@router.post("/search")
async def rag_search(
    body: SearchBody,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """RAG 语义搜索。"""
    results = await ai_service.rag_search(db, body.query, body.top_k)
    return Response.ok({"results": results})


@router.post("/analyze")
async def rag_analyze(
    body: AnalyzeBody,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """文档分析。"""
    result = await ai_service.rag_analyze(db, body.document)
    return Response.ok(result)
