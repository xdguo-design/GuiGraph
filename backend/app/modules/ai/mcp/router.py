"""MCP 管理路由。"""

from fastapi import APIRouter

from app.core.utils.response import Response

router = APIRouter()


@router.get("")
async def list_mcp_servers():
    """列出 MCP 服务器。"""
    return Response.ok({"items": []})


@router.post("")
async def register_mcp():
    """注册 MCP 服务器。"""
    return Response.ok({"message": "注册成功"})


@router.put("/{mcp_id}")
async def update_mcp(mcp_id: str):
    """更新 MCP 配置。"""
    return Response.ok({"message": "更新成功"})


@router.delete("/{mcp_id}")
async def delete_mcp(mcp_id: str):
    """删除 MCP 服务器。"""
    return Response.ok({"message": "删除成功"})


@router.post("/{mcp_id}/connect")
async def test_mcp_connection(mcp_id: str):
    """测试 MCP 连接。"""
    return Response.ok({"status": "connected"})


@router.get("/{mcp_id}/tools")
async def get_mcp_tools(mcp_id: str):
    """获取 MCP 工具列表。"""
    return Response.ok({"tools": []})
