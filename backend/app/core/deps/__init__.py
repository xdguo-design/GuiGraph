"""认证依赖模块。"""

from .auth import get_current_user, get_current_user_with_role, check_resource_permission

__all__ = ["get_current_user", "check_role", "check_resource_permission"]
