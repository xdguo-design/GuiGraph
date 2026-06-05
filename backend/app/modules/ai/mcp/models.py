"""MCP 管理模块 ORM 模型。"""

from sqlalchemy import String, Integer, Enum, JSON, Text, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base, TimestampMixin
from app.shared.enums import AuthType


class SysMcpServer(Base, TimestampMixin):
    """MCP 服务器表。"""
    __tablename__ = "sys_mcp_server"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, comment="MCP 服务器名称")
    type: Mapped[str] = mapped_column(String(20), nullable=False, comment="类型: stdio/sse/http")
    command: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="启动命令（stdio 类型）")
    args: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, comment="启动参数数组")
    url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="服务器 URL（sse/http 类型）")
    env: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="环境变量（加密存储）")
    status: Mapped[str] = mapped_column(String(20), default="offline", comment="状态: online/offline/error")
    tools: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="可用工具列表")
    error_msg: Mapped[str | None] = mapped_column(Text, nullable=True, comment="错误信息")
    created_by: Mapped[int] = mapped_column(Integer, nullable=False, comment="创建人 ID")

    tool_auths = relationship("SysMcpToolAuth", back_populates="server", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "type": self.type,
            "command": self.command,
            "args": self.args,
            "url": self.url,
            "status": self.status,
            "tools": self.tools,
            "error_msg": self.error_msg,
            "created_by": str(self.created_by),
        }


class SysMcpToolAuth(Base, TimestampMixin):
    """MCP 工具权限表。"""
    __tablename__ = "sys_mcp_tool_auth"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    mcp_server_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="MCP 服务器 ID")
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="工具名称")
    role: Mapped[str] = mapped_column(String(20), nullable=False, comment="允许的角色")

    server = relationship("SysMcpServer", back_populates="tool_auths")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "mcp_server_id": str(self.mcp_server_id),
            "tool_name": self.tool_name,
            "role": self.role,
        }
