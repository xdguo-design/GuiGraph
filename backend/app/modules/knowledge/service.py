"""知识库笔记服务层。"""

from datetime import datetime
from loguru import logger
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.knowledge.models import KnowledgeBase, Note, NoteVersion


class KnowledgeService:
    """知识库笔记业务逻辑。"""

    # ── 知识库 ──

    async def list_knowledge_bases(self, db: AsyncSession) -> list[dict]:
        rows = (await db.execute(select(KnowledgeBase).order_by(KnowledgeBase.id))).scalars().all()
        return [r.to_dict() for r in rows]

    async def get_knowledge_base(self, db: AsyncSession, kb_id: int) -> dict | None:
        row = await db.get(KnowledgeBase, kb_id)
        return row.to_dict() if row else None

    async def create_knowledge_base(self, db: AsyncSession, data: dict) -> dict:
        record = KnowledgeBase(**data)
        db.add(record)
        await db.flush()
        return record.to_dict()

    # ── 笔记 ──

    async def list_notes(self, db: AsyncSession, knowledge_base_id: int | None = None) -> list[dict]:
        q = select(Note)
        if knowledge_base_id:
            q = q.where(Note.knowledge_base_id == knowledge_base_id)
        q = q.order_by(Note.order_num, Note.id)
        rows = (await db.execute(q)).scalars().all()
        return [r.to_dict() for r in rows]

    async def get_note(self, db: AsyncSession, note_id: int) -> dict | None:
        row = await db.get(Note, note_id)
        return row.to_dict() if row else None

    async def create_note(self, db: AsyncSession, data: dict) -> dict:
        record = Note(**data)
        db.add(record)
        await db.flush()
        return record.to_dict()

    async def update_note(self, db: AsyncSession, note_id: int, data: dict, author_id: int) -> dict | None:
        record = await db.get(Note, note_id)
        if not record:
            return None
        # 保存版本历史
        version_count = (await db.execute(
            select(func.count(NoteVersion.id)).where(NoteVersion.note_id == note_id)
        )).scalar() or 0
        version = NoteVersion(
            note_id=note_id,
            version_num=version_count + 1,
            title=record.title,
            content=record.content,
            change_desc=data.get("change_desc", "更新笔记"),
            author_id=author_id,
        )
        db.add(version)

        for k, v in data.items():
            if hasattr(record, k) and k not in ("id",):
                setattr(record, k, v)
        await db.flush()
        return record.to_dict()

    async def delete_note(self, db: AsyncSession, note_id: int) -> bool:
        record = await db.get(Note, note_id)
        if not record:
            return False
        await db.delete(record)
        return True

    # ── 版本历史 ──

    async def list_note_versions(self, db: AsyncSession, note_id: int) -> list[dict]:
        rows = (await db.execute(
            select(NoteVersion).where(NoteVersion.note_id == note_id).order_by(NoteVersion.version_num.desc())
        )).scalars().all()
        return [r.to_dict() for r in rows]

    async def get_note_version(self, db: AsyncSession, version_id: int) -> dict | None:
        row = await db.get(NoteVersion, version_id)
        return row.to_dict() if row else None


knowledge_service = KnowledgeService()
