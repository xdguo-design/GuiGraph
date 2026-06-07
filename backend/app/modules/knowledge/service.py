"""知识库笔记服务层。"""

from datetime import datetime
from loguru import logger
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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

    async def get_or_create_team_knowledge_base(
        self, db: AsyncSession, team_id: int, team_name: str | None = None
    ) -> dict:
        """获取或自动创建团队知识库。"""
        code = f"team_{team_id}_changes"
        result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.code == code))
        kb = result.scalar_one_or_none()
        if kb:
            return kb.to_dict()

        display_name = team_name or f"Team{team_id}"
        kb = KnowledgeBase(
            name=f"{display_name}团队变更知识库",
            code=code,
            description=f"团队({team_id})所有变更内容的自动沉淀知识库",
            owner_id=team_id,
            owner_type="team",
            read_roles=["editor", "viewer", "auditor"],
            write_roles=["system_admin", "dept_admin", "team_admin"],
        )
        db.add(kb)
        await db.flush()
        await db.refresh(kb)
        logger.info(f"已自动创建团队知识库: {kb.name} (id={kb.id})")
        return kb.to_dict()

    # ── 笔记 ──

    async def list_notes(self, db: AsyncSession, knowledge_base_id: int | None = None) -> list[dict]:
        q = select(Note)
        if knowledge_base_id:
            q = q.where(Note.knowledge_base_id == knowledge_base_id)
        q = q.order_by(Note.order_num, Note.id)
        rows = (await db.execute(q)).scalars().all()
        return [r.to_dict() for r in rows]

    async def list_notes_by_team(self, db: AsyncSession, team_id: int) -> list[dict]:
        """根据团队 ID 查询该团队知识库下的所有笔记。"""
        from app.modules.knowledge.models import KnowledgeBase
        subq = select(KnowledgeBase.id).where(
            KnowledgeBase.owner_id == team_id,
            KnowledgeBase.owner_type == "team",
        ).scalar_subquery()
        q = select(Note).where(Note.knowledge_base_id.in_(subq)).order_by(Note.created_at.desc())
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
