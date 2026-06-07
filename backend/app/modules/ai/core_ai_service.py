"""核心 AI 服务：串联 LLM Gateway + Prompt Engine，提供业务级语义方法。"""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai import llm_gateway, prompt_engine


class CoreAIService:
    """核心 AI 服务：各业务模块通过此类调用 AI 能力。"""

    # ── 变更管理 ──────────────────────────────────────────────

    async def generate_change_doc(
        self, db: AsyncSession, changes_text: str, user_id: int = 0
    ) -> str:
        """生成变更说明书。

        Args:
            db: 数据库会话
            changes_text: 变更信息文本（可以是多条变更的汇总）
            user_id: 调用用户 ID
        """
        template = await prompt_engine.get_template(db, "change_doc_generator")
        prompt = prompt_engine.render(template, {"changes": changes_text})
        return await llm_gateway.call(
            db, scenario="change_doc_generator", prompt=prompt, user_id=user_id
        )

    async def analyze_change_impact(
        self,
        db: AsyncSession,
        content: str,
        change_type: str = "",
        effect_scope: str = "",
        user_id: int = 0,
    ) -> str:
        """分析变更影响范围。"""
        template = await prompt_engine.get_template(db, "change_impact_analysis")
        prompt = prompt_engine.render(template, {
            "content": content,
            "change_type": change_type,
            "effect_scope": effect_scope,
        })
        return await llm_gateway.call(
            db, scenario="change_impact_analysis", prompt=prompt, user_id=user_id
        )

    # ── 知识库 ────────────────────────────────────────────────

    async def smart_search(
        self, db: AsyncSession, query: str, filters: dict, user_id: int = 0
    ) -> list[dict]:
        """智能检索：超越关键词，基于上下文理解。"""
        template = await prompt_engine.get_template(db, "smart_search")
        context = "当前为测试环境，暂无实际知识库数据。"
        prompt = prompt_engine.render(template, {"context": context, "query": query})
        try:
            result = await llm_gateway.call(
                db, scenario="smart_search", prompt=prompt, user_id=user_id
            )
            return [{"title": "AI 搜索结果", "content": result, "score": 0.95}]
        except Exception as e:
            logger.warning(f"智能搜索失败: {e}")
            return []

    async def auto_tag_note(
        self, db: AsyncSession, title: str, content: str, user_id: int = 0
    ) -> list[str]:
        """为笔记自动推荐标签。"""
        template = await prompt_engine.get_template(db, "auto_tag_note")
        prompt = prompt_engine.render(template, {"title": title, "content": content[:2000]})
        try:
            result = await llm_gateway.call(
                db, scenario="auto_tag_note", prompt=prompt, user_id=user_id
            )
            # 尝试解析 JSON 数组
            import json
            tags = json.loads(result.strip().strip("```json").strip("```").strip())
            if isinstance(tags, list):
                return [str(t) for t in tags[:5]]
            return []
        except Exception as e:
            logger.warning(f"自动标签失败: {e}")
            return []

    # ── 仪表盘 ────────────────────────────────────────────────

    async def get_insights(
        self, db: AsyncSession, dashboard_data: dict, user_id: int = 0
    ) -> str:
        """仪表盘智能洞察。"""
        template = await prompt_engine.get_template(db, "dashboard_insight")
        import json
        prompt = prompt_engine.render(template, {
            "dashboard_data": json.dumps(dashboard_data, ensure_ascii=False, indent=2)
        })
        return await llm_gateway.call(
            db, scenario="dashboard_insight", prompt=prompt, user_id=user_id
        )

    # ── Jenkins ───────────────────────────────────────────────

    async def diagnose_build_failure(
        self, db: AsyncSession, build_log: str, user_id: int = 0
    ) -> str:
        """诊断构建失败原因。"""
        template = await prompt_engine.get_template(db, "build_diagnosis")
        prompt = prompt_engine.render(template, {"build_log": build_log[:8000]})
        return await llm_gateway.call(
            db, scenario="build_diagnosis", prompt=prompt, user_id=user_id
        )

    # ── Git ───────────────────────────────────────────────────

    async def generate_commit_message(
        self, db: AsyncSession, diff_text: str, user_id: int = 0
    ) -> str:
        """根据 diff 生成 commit 消息。"""
        template = await prompt_engine.get_template(db, "commit_message_gen")
        prompt = prompt_engine.render(template, {"diff_text": diff_text[:8000]})
        return await llm_gateway.call(
            db, scenario="commit_message_gen", prompt=prompt, user_id=user_id
        )

    # ── 通用 ──────────────────────────────────────────────────

    async def summarize(
        self, db: AsyncSession, content: str, user_id: int = 0
    ) -> str:
        """通用文本摘要。"""
        template = await prompt_engine.get_template(db, "summary")
        prompt = prompt_engine.render(template, {"content": content[:6000]})
        return await llm_gateway.call(
            db, scenario="smart_search", prompt=prompt, user_id=user_id
        )


# 全局单例
core_ai = CoreAIService()
