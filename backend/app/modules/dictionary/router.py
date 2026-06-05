"""字典管理路由。"""

from fastapi import APIRouter

from app.core.utils.response import Response

router = APIRouter()


@router.get("/domains")
async def list_domains():
    """获取领域列表。"""
    return Response.ok({"items": []})


@router.post("/domains")
async def create_domain():
    """创建领域。"""
    return Response.ok({"message": "创建成功"})


@router.get("/applications")
async def list_applications():
    """获取应用列表。"""
    return Response.ok({"items": []})


@router.post("/applications")
async def create_application():
    """创建应用。"""
    return Response.ok({"message": "创建成功"})


@router.get("/components")
async def list_components():
    """获取组件列表。"""
    return Response.ok({"items": []})


@router.post("/components")
async def create_component():
    """创建组件。"""
    return Response.ok({"message": "创建成功"})
