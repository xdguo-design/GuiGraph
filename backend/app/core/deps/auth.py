"""认证依赖（FastAPI Depends）。"""

from typing import Annotated, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security.jwt import verify_token
from app.core.security.wechat import wechat_client
from app.config.permissions import check_permission, Role
from app.core.database.session import get_db
from app.modules.user.models import SysUser

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> SysUser:
    """获取当前登录用户对象（从 Bearer Token 中提取）。"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效，缺少用户标识",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从数据库查询完整用户对象
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌中的用户标识无效",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = await db.execute(
        select(SysUser).where(SysUser.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_with_role(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    required_roles: list[str] = [],
):
    """获取当前用户并校验角色（从 Token 中解析 role）。"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
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
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    ) -> str:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未提供认证令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
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
