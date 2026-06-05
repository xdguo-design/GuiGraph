"""认证依赖（FastAPI Depends）。"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security.jwt import verify_token
from app.core.security.wechat import wechat_client
from app.config.permissions import check_permission, Role

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> str:
    """获取当前登录用户 ID（从 Bearer Token 中提取）。"""
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload.get("sub")


async def get_current_user_with_role(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    required_roles: list[str],
):
    """获取当前用户并校验角色（从 Token 中解析 role）。"""
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_role = payload.get("role", "editor")
    if user_role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足",
        )
    return payload


def check_resource_permission(user_role: str, resource: str, action: str) -> bool:
    """检查用户对某资源某操作的权限。"""
    if not check_permission(user_role, resource, action):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足: {resource}.{action}",
        )
    return True


def check_role(*roles: str):
    """角色检查依赖工厂。"""
    async def _check(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    ) -> str:
        payload = verify_token(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌，请重新登录",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_role = payload.get("role", "editor")
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
            )
        return payload.get("sub")
    return _check
