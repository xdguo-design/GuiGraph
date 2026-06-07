"""AI 模型管理模块 ORM 模型。"""

from sqlalchemy import String, Integer, Boolean, JSON, Float, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base, TimestampMixin


class AiModelConfig(Base, TimestampMixin):
    """AI 模型配置表。"""
    __tablename__ = "ai_model_config"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, comment="模型显示名")
    model_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="模型类型: llm/vision/embedding")
    provider: Mapped[str] = mapped_column(String(50), nullable=False, comment="提供商: zhipu/aliyun/openai/local")
    model_id: Mapped[str] = mapped_column(String(100), nullable=False, default="", comment="模型标识: glm-5.1/glm-4.7/qwen-max 等")
    tier: Mapped[str] = mapped_column(String(20), nullable=False, default="fast", comment="算力档位: complex/fast")
    env_tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, comment="环境标签: dev/test/prod/all")
    api_key_enc: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="API Key（加密存储）")
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="API 基础 URL")
    max_output_tokens: Mapped[int | None] = mapped_column(Integer, default=4096, comment="最大输出 Tokens")
    temperature: Mapped[float | None] = mapped_column(Float, default=0.7, comment="温度参数")
    rate_limit_rpm: Mapped[int] = mapped_column(Integer, default=60, comment="每分钟请求数限制")
    cost_per_1m: Mapped[float | None] = mapped_column(Float, nullable=True, comment="成本 (¥/百万 tokens)")
    priority: Mapped[int] = mapped_column(Integer, default=1, comment="同档位内优先级")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否为该档位默认模型")
    active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    created_by: Mapped[int] = mapped_column(Integer, nullable=False, comment="创建人 ID")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "model_type": self.model_type,
            "provider": self.provider,
            "model_id": self.model_id,
            "tier": self.tier,
            "env_tags": self.env_tags,
            "base_url": self.base_url,
            "max_output_tokens": self.max_output_tokens,
            "temperature": self.temperature,
            "rate_limit_rpm": self.rate_limit_rpm,
            "cost_per_1m": self.cost_per_1m,
            "priority": self.priority,
            "is_default": self.is_default,
            "active": self.active,
            "created_by": str(self.created_by),
        }


class ScenarioBinding(Base, TimestampMixin):
    """场景-模型绑定表：管理员配置每个场景使用哪个模型。"""
    __tablename__ = "scenario_binding"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scenario_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="场景名称")
    tier: Mapped[str] = mapped_column(String(20), nullable=False, default="fast", comment="推荐档位: complex/fast")
    model_config_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="关联 ai_model_config.id")
    env: Mapped[str] = mapped_column(String(20), nullable=False, default="all", comment="环境")
    priority: Mapped[int] = mapped_column(Integer, default=1, comment="优先级（降级顺序）")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "scenario_name": self.scenario_name,
            "tier": self.tier,
            "model_config_id": str(self.model_config_id),
            "env": self.env,
            "priority": self.priority,
        }


class AiUsageLog(Base, TimestampMixin):
    """AI 调用审计日志表。"""
    __tablename__ = "ai_usage_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="调用用户 ID")
    scenario: Mapped[str] = mapped_column(String(50), nullable=False, comment="场景: change_doc/smart_search/insight 等")
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="实际使用的模型名")
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, comment="输入 token 数")
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, comment="输出 token 数")
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, comment="响应耗时(ms)")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="success", comment="success/failed")
    error_msg: Mapped[str | None] = mapped_column(Text, nullable=True, comment="错误信息")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "scenario": self.scenario,
            "model_name": self.model_name,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "latency_ms": self.latency_ms,
            "status": self.status,
            "error_msg": self.error_msg,
        }


class AiPromptTemplate(Base, TimestampMixin):
    """Prompt 模板库：管理员可维护各场景的 Prompt。"""
    __tablename__ = "ai_prompt_template"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, comment="模板名: change_doc_generator")
    scenario: Mapped[str] = mapped_column(String(50), nullable=False, comment="关联场景")
    template: Mapped[str] = mapped_column(Text, nullable=False, comment="Prompt 模板，支持 {{var}} 占位符")
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0.0", comment="版本号")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "scenario": self.scenario,
            "template": self.template,
            "version": self.version,
            "is_active": self.is_active,
        }
