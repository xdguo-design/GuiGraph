"""Wiki 结构化文档路由。"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response
from app.modules.wiki.service import wiki_service

router = APIRouter()


class SpaceCreate(BaseModel):
    name: str
    key: str
    description: str = ""
    owner_id: int = 0
    visibility: str = "team"
    read_roles: list[str] = ["viewer"]
    write_roles: list[str] = ["editor"]


class DocCreate(BaseModel):
    space_id: int
    title: str
    content: str = ""
    parent_id: int | None = None
    tags: list[str] = []
    author_id: int = 0
    order_num: int = 0


class DocUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    parent_id: int | None = None
    tags: list[str] | None = None
    order_num: int | None = None
    is_published: bool | None = None
    change_desc: str = "更新文档"


# ── 空间 ──

@router.get("/spaces")
async def list_spaces(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await wiki_service.list_spaces(db)
    return Response.ok({"items": items})


@router.post("/spaces")
async def create_space(
    body: SpaceCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await wiki_service.create_space(db, body.model_dump())
    return Response.ok(item)


# ── 文档 ──

@router.get("/docs")
async def list_docs(
    space_id: int | None = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await wiki_service.list_docs(db, space_id)
    return Response.ok({"items": items})


@router.get("/{doc_id}")
async def get_doc(
    doc_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await wiki_service.get_doc(db, doc_id)
    if not item:
        raise HTTPException(status_code=404, detail="文档不存在")
    return Response.ok(item)


@router.post("/docs")
async def create_doc(
    body: DocCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = body.model_dump()
    data["author_id"] = current_user.id
    item = await wiki_service.create_doc(db, data)
    return Response.ok(item)


@router.put("/docs/{doc_id}")
async def update_doc(
    doc_id: int,
    body: DocUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = body.model_dump(exclude_none=True)
    item = await wiki_service.update_doc(db, doc_id, data, current_user.id)
    if not item:
        raise HTTPException(status_code=404, detail="文档不存在")
    return Response.ok(item)


@router.delete("/docs/{doc_id}")
async def delete_doc(
    doc_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ok = await wiki_service.delete_doc(db, doc_id)
    if not ok:
        raise HTTPException(status_code=404, detail="文档不存在")
    return Response.ok({"message": "删除成功"})
