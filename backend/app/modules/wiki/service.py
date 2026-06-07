"""Wiki 服务层。"""

from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.wiki.models import WikiSpace, WikiDoc, WikiDocVersion


class WikiService:
    """Wiki 业务逻辑。"""

    # ── 空间 ──

    async def list_spaces(self, db: AsyncSession) -> list[dict]:
        rows = (await db.execute(select(WikiSpace).order_by(WikiSpace.id))).scalars().all()
        return [r.to_dict() for r in rows]

    async def create_space(self, db: AsyncSession, data: dict) -> dict:
        record = WikiSpace(**data)
        db.add(record)
        await db.flush()
        return record.to_dict()

    # ── 文档 ──

    async def list_docs(self, db: AsyncSession, space_id: int | None = None) -> list[dict]:
        q = select(WikiDoc)
        if space_id:
            q = q.where(WikiDoc.space_id == space_id)
        q = q.order_by(WikiDoc.order_num, WikiDoc.id)
        rows = (await db.execute(q)).scalars().all()
        return [r.to_dict() for r in rows]

    async def get_doc(self, db: AsyncSession, doc_id: int) -> dict | None:
        row = await db.get(WikiDoc, doc_id)
        return row.to_dict() if row else None

    async def create_doc(self, db: AsyncSession, data: dict) -> dict:
        record = WikiDoc(**data)
        db.add(record)
        await db.flush()
        return record.to_dict()

    async def update_doc(self, db: AsyncSession, doc_id: int, data: dict, author_id: int) -> dict | None:
        record = await db.get(WikiDoc, doc_id)
        if not record:
            return None
        # 保存版本
        ver_count = (await db.execute(
            select(func.count(WikiDocVersion.id)).where(WikiDocVersion.doc_id == doc_id)
        )).scalar() or 0
        version = WikiDocVersion(
            doc_id=doc_id,
            version_num=ver_count + 1,
            title=record.title,
            content=record.content,
            change_desc=data.get("change_desc", "更新文档"),
            author_id=author_id,
        )
        db.add(version)
        for k, v in data.items():
            if hasattr(record, k) and k != "id":
                setattr(record, k, v)
        await db.flush()
        return record.to_dict()

    async def delete_doc(self, db: AsyncSession, doc_id: int) -> bool:
        record = await db.get(WikiDoc, doc_id)
        if not record:
            return False
        await db.delete(record)
        return True


wiki_service = WikiService()
