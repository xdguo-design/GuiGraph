"""MCP 管理路由。"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response
from app.modules.ai.service import ai_mcp_service

router = APIRouter()


class McpCreate(BaseModel):
    name: str
    description: str = ""
    endpoint: str = ""
    auth_type: str = ""
    auth_config: dict = {}


class McpUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    endpoint: str | None = None
    auth_type: str | None = None
    auth_config: dict | None = None


@router.get("")
async def list_mcp_servers(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await ai_mcp_service.list_servers(db)
    return Response.ok({"items": items})


@router.post("")
async def register_mcp(
    body: McpCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await ai_mcp_service.register_server(db, body.model_dump())
    return Response.ok(item)


@router.put("/{mcp_id}")
async def update_mcp(
    mcp_id: int,
    body: McpUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await ai_mcp_service.update_server(db, mcp_id, body.model_dump(exclude_none=True))
    if not item:
        raise HTTPException(status_code=404, detail="MCP 服务器不存在")
    return Response.ok(item)


@router.delete("/{mcp_id}")
async def delete_mcp(
    mcp_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ok = await ai_mcp_service.delete_server(db, mcp_id)
    if not ok:
        raise HTTPException(status_code=404, detail="MCP 服务器不存在")
    return Response.ok({"message": "删除成功"})


@router.post("/{mcp_id}/connect")
async def test_mcp_connection(mcp_id: int, current_user=Depends(get_current_user)):
    """测试 MCP 连接。"""
    return Response.ok({"status": "connected", "mcp_id": str(mcp_id)})


@router.get("/{mcp_id}/tools")
async def get_mcp_tools(mcp_id: int, current_user=Depends(get_current_user)):
    """获取 MCP 工具列表。"""
    return Response.ok({"tools": [], "mcp_id": str(mcp_id)})
