"""权限矩阵配置。"""

from enum import Enum


class Role(str, Enum):
    """系统角色。"""
    SYSTEM_ADMIN = "system_admin"       # 系统管理员
    DEPT_ADMIN = "dept_admin"           # 部门管理员
    TEAM_ADMIN = "team_admin"           # 团队管理员
    EDITOR = "editor"                   # 编辑者
    VIEWER = "viewer"                   # 查看者
    AUDITOR = "auditor"                 # 审计员


# 权限矩阵：角色 -> 资源 -> 操作 -> 允许
PERMISSION_MATRIX: dict[str, dict[str, set[str]]] = {
    Role.SYSTEM_ADMIN: {
        "org": {"create", "read", "update", "delete", "manage_members"},
        "change": {"create", "read", "update", "delete", "approve"},
        "git": {"add_repo", "auth_user", "view_branches", "merge", "create_branch", "delete_branch"},
        "jenkins": {"configure", "trigger", "stop", "view_log"},
        "ai": {"search", "generate", "analyze", "manage_model", "manage_skill", "manage_mcp"},
        "audit": {"view"},
        "upgrade": {"view", "rollback", "export"},
        "minio": {"manage"},
        "mcp": {"register", "configure", "test", "delete", "view_stats"},
    },
    Role.DEPT_ADMIN: {
        "org": {"create", "read", "update", "manage_members"},  # 仅限本部门
        "change": {"create", "read", "update", "approve"},
        "git": {"add_repo", "auth_user", "view_branches", "merge"},
        "jenkins": {"trigger", "stop", "view_log"},
        "ai": {"search", "generate", "analyze"},
        "audit": {"view"},
        "upgrade": {"view", "export"},
        "mcp": {"view_stats"},
    },
    Role.TEAM_ADMIN: {
        "org": {"create", "read", "update", "manage_members"},  # 仅限本团队
        "change": {"create", "read", "update", "approve"},
        "git": {"add_repo", "auth_user", "view_branches", "merge"},
        "jenkins": {"trigger", "stop", "view_log"},
        "ai": {"search", "generate", "analyze"},
        "upgrade": {"view"},
    },
    Role.EDITOR: {
        "change": {"create", "read", "update"},
        "git": {"view_branches", "merge"},
        "jenkins": {"trigger", "view_log"},
        "ai": {"search", "generate", "analyze"},
        "upgrade": {"view"},
    },
    Role.VIEWER: {
        "change": {"read"},
        "git": {"view_branches"},
        "jenkins": {"view_log"},
        "ai": {"search", "generate"},
        "upgrade": {"view"},
    },
    Role.AUDITOR: {
        "change": {"read"},
        "git": {"view_branches"},
        "jenkins": {"view_log"},
        "ai": {"search"},
        "audit": {"view", "export"},
        "upgrade": {"view", "export"},
        "mcp": {"view_stats"},
    },
}


def check_permission(role: str, resource: str, action: str) -> bool:
    """检查角色是否拥有某资源的某操作权限。"""
    role_perms = PERMISSION_MATRIX.get(role, {})
    resource_perms = role_perms.get(resource, set())
    return action in resource_perms
