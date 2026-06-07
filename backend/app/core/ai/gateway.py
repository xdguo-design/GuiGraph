"""LLM Gateway：统一 LLM 调用入口，负责模型路由、重试、降级。"""

import time
from typing import Any

import httpx
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.model_manager.models import AiModelConfig, ScenarioBinding

# ── 场景 → 推荐档位映射 ──────────────────────────────────────
SCENARIO_TIER_HINT: dict[str, str] = {
    # complex 档（复杂推理、长文本生成）
    "change_doc_generator": "complex",
    "change_impact_analysis": "complex",
    "code_review": "complex",
    "merge_conflict_solve": "complex",
    # fast 档（快速响应、简单任务）
    "smart_search": "fast",
    "build_diagnosis": "fast",
    "dashboard_insight": "fast",
    "auto_tag_note": "fast",
    "commit_message_gen": "fast",
}

# ── 智谱 API 调用封装 ────────────────────────────────────────

ZHIPU_CHAT_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"


async def _call_zhipu(
    api_key: str,
    model_id: str,
    messages: list[dict],
    base_url: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> dict:
    """调用智谱 GLM API。"""
    url = base_url or ZHIPU_CHAT_URL
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()


# ── 通用 OpenAI 兼容调用（适配其他提供商） ───────────────────

async def _call_openai_compatible(
    api_key: str,
    model_id: str,
    messages: list[dict],
    base_url: str,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> dict:
    """调用 OpenAI 兼容 API（通义千问等国内模型大多兼容）。"""
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()


# ── LLM Gateway ──────────────────────────────────────────────


class LLMGateway:
    """统一 LLM 调用网关。

    - 根据 scenario 查询推荐档位（complex/fast）
    - 从数据库查询该档位下可用模型（按 is_default、priority 排序）
    - 按优先级依次尝试调用，支持自动降级
    - 记录调用审计日志
    """

    async def _select_models(self, db: AsyncSession, tier: str) -> list[AiModelConfig]:
        """查询指定档位的可用模型，按默认和优先级排序。"""
        stmt = (
            select(AiModelConfig)
            .where(
                AiModelConfig.tier == tier,
                AiModelConfig.active == True,  # noqa: E712
            )
            .order_by(
                AiModelConfig.is_default.desc(),
                AiModelConfig.priority.asc(),
            )
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def _get_binding_model(self, db: AsyncSession, scenario: str) -> AiModelConfig | None:
        """查询场景绑定的模型（优先于档位默认）。"""
        stmt = (
            select(ScenarioBinding, AiModelConfig)
            .join(AiModelConfig, ScenarioBinding.model_config_id == AiModelConfig.id)
            .where(
                ScenarioBinding.scenario_name == scenario,
                AiModelConfig.active == True,  # noqa: E712
            )
            .order_by(ScenarioBinding.priority.asc())
        )
        result = await db.execute(stmt)
        row = result.first()
        if row:
            return row[1]
        return None

    async def _invoke_model(self, model: AiModelConfig, messages: list[dict]) -> dict:
        """根据 provider 类型调用对应 API。"""
        api_key = model.api_key_enc or ""  # TODO: 解密
        base_url = model.base_url
        model_id = model.model_id
        temperature = model.temperature or 0.7
        max_tokens = model.max_output_tokens or 4096

        if model.provider == "zhipu":
            return await _call_zhipu(
                api_key=api_key,
                model_id=model_id,
                messages=messages,
                base_url=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            # 其他提供商走 OpenAI 兼容接口
            return await _call_openai_compatible(
                api_key=api_key,
                model_id=model_id,
                messages=messages,
                base_url=base_url or "https://open.bigmodel.cn/api/paas/v4",
                temperature=temperature,
                max_tokens=max_tokens,
            )

    async def call(
        self,
        db: AsyncSession,
        scenario: str,
        prompt: str,
        system_prompt: str = "你是一个专业的助手。",
        user_id: int = 0,
        **kwargs: Any,
    ) -> str:
        """统一调用入口：scenario → 模型路由 → 调用 → 审计。"""
        tier = SCENARIO_TIER_HINT.get(scenario, "fast")

        # 1. 优先查场景绑定
        chosen = await self._get_binding_model(db, scenario)

        # 2. 无绑定时按档位查可用模型
        if not chosen:
            models = await self._select_models(db, tier)
            if not models:
                # 3. 降级：尝试另一档位
                fallback_tier = "fast" if tier == "complex" else "complex"
                models = await self._select_models(db, fallback_tier)
            if not models:
                raise ValueError(f"没有可用的 AI 模型（场景: {scenario}，档位: {tier}）")
            chosen = models[0]

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        start_ms = int(time.time() * 1000)
        try:
            result = await self._invoke_model(chosen, messages)
            latency_ms = int(time.time() * 1000) - start_ms

            # 提取回复文本
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = result.get("usage", {})

            # 审计日志
            await self._log_usage(
                db=db,
                user_id=user_id,
                scenario=scenario,
                model_name=chosen.name,
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
                latency_ms=latency_ms,
                status="success",
            )
            return content

        except Exception as e:
            latency_ms = int(time.time() * 1000) - start_ms
            logger.error(f"LLM 调用失败: scenario={scenario}, model={chosen.name}, error={e}")
            await self._log_usage(
                db=db,
                user_id=user_id,
                scenario=scenario,
                model_name=chosen.name,
                latency_ms=latency_ms,
                status="failed",
                error_msg=str(e),
            )
            raise

    async def _log_usage(self, db: AsyncSession, **kwargs: Any) -> None:
        """记录调用审计日志。"""
        try:
            log = AiUsageLog(**kwargs)
            db.add(log)
            await db.flush()
        except Exception as e:
            logger.warning(f"AI 审计日志写入失败: {e}")


# 全局单例
llm_gateway = LLMGateway()
