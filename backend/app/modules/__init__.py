"""模块路由统一导出（MVP）。"""

from app.modules.auth.router import router as auth_router
from app.modules.user.router import router as user_router
from app.modules.organization.router import router as org_router
from app.modules.change.router import router as change_router
from app.modules.git.router import router as git_router
from app.modules.jenkins.router import router as jenkins_router

__all__ = ["auth_router", "user_router", "org_router", "change_router", "git_router", "jenkins_router"]
