"""AI 模型管理路由：模型 CRUD + 场景绑定 + Prompt 模板 + 用量查询。"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response
from app.modules.ai.service import (
    ai_model_service,
    ai_scenario_service,
    ai_prompt_service,
)
from app.core.ai import usage_logger

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────

class ModelCreate(BaseModel):
    name: str
    provider: str = "zhipu"
    model_id: str = ""
    model_type: str = "llm"
    tier: str = "fast"
    env_tags: list[str] = ["all"]
    api_key: str = ""
    base_url: str = ""
    max_output_tokens: int = 4096
    temperature: float = 0.7
    rate_limit_rpm: int = 60
    cost_per_1m: float | None = None
    priority: int = 1
    is_default: bool = False


class ModelUpdate(BaseModel):
    name: str | None = None
    provider: str | None = None
    model_id: str | None = None
    model_type: str | None = None
    tier: str | None = None
    env_tags: list[str] | None = None
    api_key: str | None = None
    base_url: str | None = None
    max_output_tokens: int | None = None
    temperature: float | None = None
    rate_limit_rpm: int | None = None
    cost_per_1m: float | None = None
    priority: int | None = None
    is_default: bool | None = None
    active: bool | None = None


class ScenarioBindingCreate(BaseModel):
    scenario_name: str
    tier: str = "fast"
    model_config_id: int
    env: str = "all"
    priority: int = 1


class ScenarioBindingUpdate(BaseModel):
    scenario_name: str | None = None
    tier: str | None = None
    model_config_id: int | None = None
    env: str | None = None
    priority: int | None = None


class PromptTemplateCreate(BaseModel):
    name: str
    scenario: str
    template: str
    version: str = "1.0.0"


class PromptTemplateUpdate(BaseModel):
    name: str | None = None
    template: str | None = None
    version: str | None = None
    is_active: bool | None = None


# ── 模型管理 ─────────────────────────────────────────────────

@router.get("")
async def list_models(
    tier: str = "",
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取模型列表，支持按档位筛选。"""
    if tier:
        items = await ai_model_service.list_models_by_tier(db, tier)
    else:
        items = await ai_model_service.list_models(db)
    return Response.ok({"items": items})


@router.post("")
async def create_model(
    body: ModelCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加模型。"""
    data = body.model_dump()
    data["api_key_enc"] = data.pop("api_key", "")
    data["created_by"] = current_user.id
    item = await ai_model_service.create_model(db, data)
    return Response.ok(item)


@router.put("/{model_id}")
async def update_model(
    model_id: int,
    body: ModelUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新模型配置。"""
    data = body.model_dump(exclude_none=True)
    if "api_key" in data:
        data["api_key_enc"] = data.pop("api_key")
    item = await ai_model_service.update_model(db, model_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="模型不存在")
    return Response.ok(item)


@router.delete("/{model_id}")
async def delete_model(
    model_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除模型。"""
    ok = await ai_model_service.delete_model(db, model_id)
    if not ok:
        raise HTTPException(status_code=404, detail="模型不存在")
    return Response.ok({"message": "删除成功"})


# ── 场景绑定 ─────────────────────────────────────────────────

@router.get("/scenarios")
async def list_scenarios(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取场景绑定列表。"""
    items = await ai_scenario_service.list_bindings(db)
    return Response.ok({"items": items})


@router.post("/scenarios")
async def create_scenario_binding(
    body: ScenarioBindingCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建场景绑定。"""
    item = await ai_scenario_service.create_binding(db, body.model_dump())
    return Response.ok(item)


@router.put("/scenarios/{binding_id}")
async def update_scenario_binding(
    binding_id: int,
    body: ScenarioBindingUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新场景绑定。"""
    item = await ai_scenario_service.update_binding(db, binding_id, body.model_dump(exclude_none=True))
    if not item:
        raise HTTPException(status_code=404, detail="绑定不存在")
    return Response.ok(item)


@router.delete("/scenarios/{binding_id}")
async def delete_scenario_binding(
    binding_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除场景绑定。"""
    ok = await ai_scenario_service.delete_binding(db, binding_id)
    if not ok:
        raise HTTPException(status_code=404, detail="绑定不存在")
    return Response.ok({"message": "删除成功"})


# ── Prompt 模板 ──────────────────────────────────────────────

@router.get("/prompts")
async def list_prompts(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取 Prompt 模板列表。"""
    items = await ai_prompt_service.list_templates(db)
    return Response.ok({"items": items})


@router.post("/prompts")
async def create_prompt(
    body: PromptTemplateCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建 Prompt 模板。"""
    item = await ai_prompt_service.create_template(db, body.model_dump())
    return Response.ok(item)


@router.put("/prompts/{template_id}")
async def update_prompt(
    template_id: int,
    body: PromptTemplateUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新 Prompt 模板。"""
    item = await ai_prompt_service.update_template(db, template_id, body.model_dump(exclude_none=True))
    if not item:
        raise HTTPException(status_code=404, detail="模板不存在")
    return Response.ok(item)


# ── 用量统计 ─────────────────────────────────────────────────

@router.get("/usage")
async def get_usage(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取 AI 调用量统计。"""
    summary = await usage_logger.get_usage_summary(db)
    return Response.ok(summary)


@router.get("/usage/logs")
async def get_usage_logs(
    limit: int = 50,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取最近的 AI 调用日志。"""
    logs = await usage_logger.get_recent_logs(db, limit=limit)
    return Response.ok({"items": logs})
