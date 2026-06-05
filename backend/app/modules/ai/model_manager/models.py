"""AI 模型管理模块 ORM 模型。"""

from sqlalchemy import String, Integer, Boolean, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base, TimestampMixin


class AiModelConfig(Base, TimestampMixin):
    """AI 模型配置表。"""
    __tablename__ = "ai_model_config"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, comment="模型名称")
    model_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="模型类型: llm/vision/embedding")
    provider: Mapped[str] = mapped_column(String(50), nullable=False, comment="提供商: openai/anthropic/aliyun/local")
    env_tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, comment="环境标签: dev/test/prod/all/cost_saving")
    api_key_enc: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="API Key（加密存储）")
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="API 基础 URL")
    max_output_tokens: Mapped[int | None] = mapped_column(Integer, default=4096, comment="最大输出 Tokens")
    temperature: Mapped[float | None] = mapped_column(Float, default=0.7, comment="温度参数")
    priority: Mapped[int] = mapped_column(Integer, default=1, comment="优先级")
    cost_per_1k: Mapped[float | None] = mapped_column(Float, nullable=True, comment="成本 (¥/1K tokens)")
    active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    created_by: Mapped[int] = mapped_column(Integer, nullable=False, comment="创建人 ID")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "model_type": self.model_type,
            "provider": self.provider,
            "env_tags": self.env_tags,
            "max_output_tokens": self.max_output_tokens,
            "temperature": self.temperature,
            "priority": self.priority,
            "cost_per_1k": self.cost_per_1k,
            "active": self.active,
            "created_by": str(self.created_by),
        }


class ScenarioBinding(Base, TimestampMixin):
    """场景-模型绑定表。"""
    __tablename__ = "scenario_binding"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scenario_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="场景名称")
    model_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="模型 ID")
    env: Mapped[str] = mapped_column(String(20), nullable=False, comment="环境")
    priority: Mapped[int] = mapped_column(Integer, default=1, comment="优先级")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "scenario_name": self.scenario_name,
            "model_id": str(self.model_id),
            "env": self.env,
            "priority": self.priority,
        }
