"""AI 服务层。"""

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.model_manager.models import AiModelConfig, ScenarioBinding
from app.modules.ai.skill.models import AiSkill
from app.modules.ai.mcp.models import SysMcpServer


class AIService:
    """AI 业务逻辑。"""

    async def rag_search(self, db: AsyncSession, query: str, top_k: int = 5) -> list[dict]:
        """RAG 语义搜索。"""
        logger.info(f"RAG 搜索: query={query}")
        # TODO: 接入 RAGFlow 客户端
        return []

    async def rag_analyze(self, db: AsyncSession, document: str) -> dict:
        """文档分析。"""
        logger.info(f"文档分析: doc_len={len(document)}")
        # TODO: 接入 AI 模型
        return {"analysis": "分析结果待实现", "summary": "", "entities": [], "keywords": []}

    async def generate_summary(self, db: AsyncSession, content: str) -> dict:
        """生成总结。"""
        logger.info(f"生成总结: content_len={len(content)}")
        # TODO: 接入 AI 模型
        return {"summary": "总结内容待实现"}


ai_service = AIService()


class AIModelService:
    """AI 模型管理业务逻辑。"""

    async def list_models(self, db: AsyncSession) -> list[dict]:
        rows = (await db.execute(select(AiModelConfig).order_by(AiModelConfig.id))).scalars().all()
        return [r.to_dict() for r in rows]

    async def create_model(self, db: AsyncSession, data: dict) -> dict:
        record = AiModelConfig(**data)
        db.add(record)
        await db.flush()
        return record.to_dict()

    async def update_model(self, db: AsyncSession, model_id: int, data: dict) -> dict | None:
        record = await db.get(AiModelConfig, model_id)
        if not record:
            return None
        for k, v in data.items():
            if hasattr(record, k) and k != "id":
                setattr(record, k, v)
        await db.flush()
        return record.to_dict()

    async def delete_model(self, db: AsyncSession, model_id: int) -> bool:
        record = await db.get(AiModelConfig, model_id)
        if not record:
            return False
        await db.delete(record)
        return True


ai_model_service = AIModelService()


class AISkillService:
    """AI Skill 管理业务逻辑。"""

    async def list_skills(self, db: AsyncSession) -> list[dict]:
        rows = (await db.execute(select(AiSkill).order_by(AiSkill.id))).scalars().all()
        return [r.to_dict() for r in rows]

    async def enable_skill(self, db: AsyncSession, skill_id: int) -> bool:
        record = await db.get(AiSkill, skill_id)
        if not record:
            return False
        record.is_enabled = True
        await db.flush()
        return True

    async def disable_skill(self, db: AsyncSession, skill_id: int) -> bool:
        record = await db.get(AiSkill, skill_id)
        if not record:
            return False
        record.is_enabled = False
        await db.flush()
        return True


ai_skill_service = AISkillService()


class AIMcpService:
    """AI MCP 管理业务逻辑。"""

    async def list_servers(self, db: AsyncSession) -> list[dict]:
        rows = (await db.execute(select(SysMcpServer).order_by(SysMcpServer.id))).scalars().all()
        return [r.to_dict() for r in rows]

    async def register_server(self, db: AsyncSession, data: dict) -> dict:
        record = SysMcpServer(**data)
        db.add(record)
        await db.flush()
        return record.to_dict()

    async def update_server(self, db: AsyncSession, mcp_id: int, data: dict) -> dict | None:
        record = await db.get(SysMcpServer, mcp_id)
        if not record:
            return None
        for k, v in data.items():
            if hasattr(record, k) and k != "id":
                setattr(record, k, v)
        await db.flush()
        return record.to_dict()

    async def delete_server(self, db: AsyncSession, mcp_id: int) -> bool:
        record = await db.get(SysMcpServer, mcp_id)
        if not record:
            return False
        await db.delete(record)
        return True


ai_mcp_service = AIMcpService()
