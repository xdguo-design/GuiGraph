"""看板/时间线路由。"""

from fastapi import APIRouter, Depends

from app.core.deps.auth import get_current_user
from app.core.utils.response import Response

router = APIRouter()


@router.get("")
async def get_dashboard(user_id: str = Depends(get_current_user)):
    """获取仪表盘数据。"""
    return Response.ok({
        "stats": {
            "total_changes": 0,
            "pending_changes": 0,
            "released_changes": 0,
        },
        "recent_changes": [],
    })


@router.get("/timeline")
async def get_timeline(
    func_point_id: str = "",
    version_id: str = "",
    user_id: str = Depends(get_current_user),
):
    """获取时间线。"""
    return Response.ok({"items": []})
