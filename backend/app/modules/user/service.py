"""用户模块服务层。"""

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.models import SysUser


class UserService:
    """用户业务逻辑。"""

    async def get_user(self, db: AsyncSession, user_id: int) -> dict | None:
        """获取用户信息。"""
        row = await db.get(SysUser, user_id)
        return row.to_dict() if row else None

    async def get_user_by_username(self, db: AsyncSession, username: str) -> SysUser | None:
        """通过用户名查询用户。"""
        result = await db.execute(
            select(SysUser).where(SysUser.username == username)
        )
        return result.scalar_one_or_none()

    async def update_user(self, user_id: int, data: dict) -> bool:
        """更新用户信息。"""
        logger.info(f"更新用户: {user_id}")
        return True

    async def bind_wechat(self, user_id: str, openid: str, unionid: str) -> bool:
        """绑定微信账号。"""
        logger.info(f"绑定微信: user={user_id}, openid={openid}")
        return True
