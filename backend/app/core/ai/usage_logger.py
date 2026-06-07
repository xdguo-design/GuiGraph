"""AI 调用审计日志服务。"""

from typing import Any

from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.model_manager.models import AiUsageLog


class UsageLogger:
    """AI 调用量查询服务。"""

    async def get_usage_summary(
        self,
        db: AsyncSession,
        user_id: int | None = None,
        scenario: str | None = None,
    ) -> dict:
        """查询 AI 调用汇总。"""
        conditions = []
        if user_id:
            conditions.append(AiUsageLog.user_id == user_id)
        if scenario:
            conditions.append(AiUsageLog.scenario == scenario)

        # 总调用次数
        count_stmt = select(func.count(AiUsageLog.id))
        if conditions:
            from sqlalchemy import and_
            count_stmt = count_stmt.where(and_(*conditions))
        total = (await db.execute(count_stmt)).scalar() or 0

        # 总 token 消耗
        token_stmt = select(
            func.sum(AiUsageLog.input_tokens),
            func.sum(AiUsageLog.output_tokens),
        )
        if conditions:
            from sqlalchemy import and_
            token_stmt = token_stmt.where(and_(*conditions))
        token_result = (await db.execute(token_stmt)).one()
        total_input = token_result[0] or 0
        total_output = token_result[1] or 0

        # 按场景统计
        by_scenario_stmt = (
            select(
                AiUsageLog.scenario,
                func.count(AiUsageLog.id).label("count"),
            )
            .group_by(AiUsageLog.scenario)
        )
        by_scenario = {
            row[0]: row[1]
            for row in (await db.execute(by_scenario_stmt)).all()
        }

        return {
            "total_calls": total,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "by_scenario": by_scenario,
        }

    async def get_recent_logs(
        self,
        db: AsyncSession,
        limit: int = 50,
    ) -> list[dict]:
        """查询最近的调用日志。"""
        stmt = (
            select(AiUsageLog)
            .order_by(AiUsageLog.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        return [log.to_dict() for log in result.scalars().all()]


# 全局单例
usage_logger = UsageLogger()
