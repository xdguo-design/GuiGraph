"""审计日志模块 ORM 模型。"""

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base


class AuditLog(Base):
    """审计日志表。"""
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, nullable=False, comment="操作时间")
    user_id: Mapped[str] = mapped_column(String(50), nullable=False, comment="操作用户 ID")
    agent_role: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="Agent 角色")
    operation: Mapped[str] = mapped_column(String(50), nullable=False, comment="操作类型")
    resource: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="操作资源")
    result: Mapped[str] = mapped_column(String(20), nullable=False, comment="操作结果")
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="来源 IP")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "user_id": self.user_id,
            "agent_role": self.agent_role,
            "operation": self.operation,
            "resource": self.resource,
            "result": self.result,
            "ip_address": self.ip_address,
        }
