"""知识库笔记路由。"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response
from app.modules.knowledge.service import knowledge_service

router = APIRouter()


# ── Schemas ──

class KnowledgeBaseCreate(BaseModel):
    name: str
    code: str
    description: str = ""
    owner_id: int = 0
    owner_type: str = "team"
    read_roles: list[str] = ["viewer"]
    write_roles: list[str] = ["editor"]


class NoteCreate(BaseModel):
    knowledge_base_id: int
    title: str
    content: str = ""
    parent_note_id: int | None = None
    order_num: int = 0
    tags: list[str] = []
    author_id: int = 0


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    parent_note_id: int | None = None
    order_num: int | None = None
    tags: list[str] | None = None
    is_published: bool | None = None
    change_desc: str = "更新笔记"


# ── 知识库 ──

@router.get("/bases")
async def list_knowledge_bases(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await knowledge_service.list_knowledge_bases(db)
    return Response.ok({"items": items})


@router.get("/bases/{kb_id}")
async def get_knowledge_base(
    kb_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await knowledge_service.get_knowledge_base(db, kb_id)
    if not item:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return Response.ok(item)


@router.post("/bases")
async def create_knowledge_base(
    body: KnowledgeBaseCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await knowledge_service.create_knowledge_base(db, body.model_dump())
    return Response.ok(item)


# ── 笔记 ──

@router.get("/notes")
async def list_notes(
    knowledge_base_id: int | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await knowledge_service.list_notes(db, knowledge_base_id)
    return Response.ok({"items": items})


@router.get("/notes/{note_id}")
async def get_note(
    note_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await knowledge_service.get_note(db, note_id)
    if not item:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return Response.ok(item)


@router.post("/notes")
async def create_note(
    body: NoteCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = body.model_dump()
    data["author_id"] = current_user.id
    item = await knowledge_service.create_note(db, data)
    return Response.ok(item)


@router.put("/notes/{note_id}")
async def update_note(
    note_id: int,
    body: NoteUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = body.model_dump(exclude_none=True)
    item = await knowledge_service.update_note(db, note_id, data, current_user.id)
    if not item:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return Response.ok(item)


@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ok = await knowledge_service.delete_note(db, note_id)
    if not ok:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return Response.ok({"message": "删除成功"})


# ── 版本历史 ──

@router.get("/notes/{note_id}/versions")
async def list_note_versions(
    note_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await knowledge_service.list_note_versions(db, note_id)
    return Response.ok({"items": items})


@router.post("/notes/{note_id}/ai-generate")
async def ai_generate_note(
    note_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI 生成笔记草稿（占位）。"""
    note = await knowledge_service.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return Response.ok({"message": "AI 生成功能待接入", "note_id": str(note_id)})
