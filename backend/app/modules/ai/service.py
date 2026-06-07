"""AI 服务层：串联 Gateway + Prompt Engine，对外提供语义化方法。"""

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai import llm_gateway, prompt_engine
from app.modules.ai.model_manager.models import (
    AiModelConfig,
    ScenarioBinding,
    AiPromptTemplate,
    AiUsageLog,
)
from app.modules.ai.skill.models import AiSkill
from app.modules.ai.mcp.models import SysMcpServer
from app.modules.ai.core_ai_service import CoreAIService


# ── 向后兼容的旧服务类 ──────────────────────────────────────

class AIService:
    """AI 业务逻辑（旧接口兼容）。"""

    async def rag_search(self, db: AsyncSession, query: str, top_k: int = 5) -> list[dict]:
        """RAG 语义搜索。"""
        logger.info(f"RAG 搜索: query={query}")
        return await core_ai.smart_search(db, query, {})

    async def rag_analyze(self, db: AsyncSession, document: str) -> dict:
        """文档分析。"""
        logger.info(f"文档分析: doc_len={len(document)}")
        result = await core_ai.summarize(db, document)
        return {"analysis": result, "summary": result, "entities": [], "keywords": []}

    async def generate_summary(self, db: AsyncSession, content: str) -> dict:
        """生成总结。"""
        logger.info(f"生成总结: content_len={len(content)}")
        result = await core_ai.summarize(db, content)
        return {"summary": result}


ai_service = AIService()


class AIModelService:
    """AI 模型管理业务逻辑。"""

    async def list_models(self, db: AsyncSession) -> list[dict]:
        rows = (await db.execute(select(AiModelConfig).order_by(AiModelConfig.id))).scalars().all()
        return [r.to_dict() for r in rows]

    async def list_models_by_tier(self, db: AsyncSession, tier: str) -> list[dict]:
        rows = (
            await db.execute(
                select(AiModelConfig)
                .where(AiModelConfig.tier == tier, AiModelConfig.active == True)  # noqa: E712
                .order_by(AiModelConfig.is_default.desc(), AiModelConfig.priority)
            )
        ).scalars().all()
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


# ── 场景绑定服务 ──────────────────────────────────────────────

class AIScenarioService:
    """场景-模型绑定管理。"""

    async def list_bindings(self, db: AsyncSession) -> list[dict]:
        rows = (await db.execute(select(ScenarioBinding).order_by(ScenarioBinding.id))).scalars().all()
        result = []
        for r in rows:
            d = r.to_dict()
            # 补充模型名
            model = await db.get(AiModelConfig, r.model_config_id)
            d["model_name"] = model.name if model else "未知"
            result.append(d)
        return result

    async def create_binding(self, db: AsyncSession, data: dict) -> dict:
        record = ScenarioBinding(**data)
        db.add(record)
        await db.flush()
        return record.to_dict()

    async def update_binding(self, db: AsyncSession, binding_id: int, data: dict) -> dict | None:
        record = await db.get(ScenarioBinding, binding_id)
        if not record:
            return None
        for k, v in data.items():
            if hasattr(record, k) and k != "id":
                setattr(record, k, v)
        await db.flush()
        return record.to_dict()

    async def delete_binding(self, db: AsyncSession, binding_id: int) -> bool:
        record = await db.get(ScenarioBinding, binding_id)
        if not record:
            return False
        await db.delete(record)
        return True


ai_scenario_service = AIScenarioService()


# ── Prompt 模板服务 ──────────────────────────────────────────

class AIPromptService:
    """Prompt 模板管理。"""

    async def list_templates(self, db: AsyncSession) -> list[dict]:
        rows = (await db.execute(select(AiPromptTemplate).order_by(AiPromptTemplate.id))).scalars().all()
        return [r.to_dict() for r in rows]

    async def create_template(self, db: AsyncSession, data: dict) -> dict:
        record = AiPromptTemplate(**data)
        db.add(record)
        await db.flush()
        return record.to_dict()

    async def update_template(self, db: AsyncSession, template_id: int, data: dict) -> dict | None:
        record = await db.get(AiPromptTemplate, template_id)
        if not record:
            return None
        for k, v in data.items():
            if hasattr(record, k) and k != "id":
                setattr(record, k, v)
        await db.flush()
        return record.to_dict()


ai_prompt_service = AIPromptService()
