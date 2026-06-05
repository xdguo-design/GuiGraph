"""审计日志 Schema 定义。"""

from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    """审计日志响应。"""
    id: str
    timestamp: str
    user_id: str
    agent_role: str
    operation: str
    resource: str
    result: str
    ip_address: str
