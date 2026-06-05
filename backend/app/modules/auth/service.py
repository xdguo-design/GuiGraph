from sqlalchemy import select

from app.core.database.session import AsyncSessionLocal
from app.core.security.crypto import hash_password, verify_password
from app.modules.user.models import SysUser
from app.shared.enums import LoginMethod, UserStatus


class AuthService:

    async def authenticate_user(self, username: str, password: str) -> dict | None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(SysUser).where(SysUser.username == username)
            )
            user = result.scalar_one_or_none()
            if not user:
                return None
            if user.password_hash and verify_password(password, user.password_hash):
                return {"id": str(user.id), "username": user.username, "role": "system_admin"}
            return None

    async def create_user(
        self,
        username: str,
        password: str,
        nickname: str = "",
        role: str = "editor",
    ) -> dict:
        pwd_hash = hash_password(password)
        async with AsyncSessionLocal() as session:
            user = SysUser(
                username=username,
                nickname=nickname or username,
                password_hash=pwd_hash,
                login_method=LoginMethod.PASSWORD,
                status=UserStatus.ACTIVE,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return {"id": str(user.id), "username": user.username}

    async def ensure_admin_user(self, username: str, password: str, nickname: str) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(SysUser).where(SysUser.username == username)
            )
            user = result.scalar_one_or_none()
            if user:
                return False
            pwd_hash = hash_password(password)
            admin = SysUser(
                username=username,
                nickname=nickname,
                password_hash=pwd_hash,
                login_method=LoginMethod.PASSWORD,
                status=UserStatus.ACTIVE,
            )
            session.add(admin)
            await session.commit()
            return True

    async def logout(self, user_id: str, token: str) -> None:
        logger.info(f"用户退出: {user_id}")


auth_service = AuthService()
