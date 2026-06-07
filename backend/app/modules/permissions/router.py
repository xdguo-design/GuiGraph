"""权限矩阵路由。"""

from fastapi import APIRouter, Depends
from app.core.deps.auth import get_current_user
from app.core.utils.response import Response

router = APIRouter()


@router.get("/matrix")
async def get_permission_matrix(
    current_user=Depends(get_current_user),
):
    """获取权限矩阵。"""
    # 返回前端 usePermission.ts 中定义的权限矩阵数据
    matrix = {
        "system_admin": {
            "org": ["create", "read", "update", "delete", "manage_members"],
            "change": ["create", "read", "update", "delete", "approve"],
            "git": ["add_repo", "auth_user", "view_branches", "merge", "create_branch", "delete_branch"],
            "jenkins": ["configure", "trigger", "stop", "view_log"],
            "ai": ["search", "generate", "analyze", "manage_model", "manage_skill", "manage_mcp"],
            "audit": ["view"],
            "upgrade": ["view", "rollback", "export"],
            "minio": ["manage"],
            "mcp": ["register", "configure", "test", "delete", "view_stats"],
        },
        "dept_admin": {
            "org": ["create", "read", "update", "manage_members"],
            "change": ["create", "read", "update", "approve"],
            "git": ["add_repo", "auth_user", "view_branches", "merge"],
            "jenkins": ["trigger", "stop", "view_log"],
            "ai": ["search", "generate", "analyze"],
            "audit": ["view"],
            "upgrade": ["view", "export"],
            "mcp": ["view_stats"],
        },
        "team_admin": {
            "org": ["create", "read", "update", "manage_members"],
            "change": ["create", "read", "update", "approve"],
            "git": ["add_repo", "auth_user", "view_branches", "merge"],
            "jenkins": ["trigger", "stop", "view_log"],
            "ai": ["search", "generate", "analyze"],
            "upgrade": ["view"],
        },
        "editor": {
            "change": ["create", "read", "update"],
            "git": ["view_branches", "merge"],
            "jenkins": ["trigger", "view_log"],
            "ai": ["search", "generate", "analyze"],
            "upgrade": ["view"],
        },
        "viewer": {
            "change": ["read"],
            "git": ["view_branches"],
            "jenkins": ["view_log"],
            "ai": ["search", "generate"],
            "upgrade": ["view"],
        },
        "auditor": {
            "change": ["read"],
            "git": ["view_branches"],
            "jenkins": ["view_log"],
            "ai": ["search"],
            "audit": ["view", "export"],
            "upgrade": ["view", "export"],
            "mcp": ["view_stats"],
        },
    }
    return Response.ok(matrix)