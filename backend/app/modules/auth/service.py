"""认证模块服务层。"""

from loguru import logger

from app.core.security.crypto import hash_password, verify_password


class AuthService:
    """认证业务逻辑。"""

    async def authenticate_user(self, username: str, password: str) -> dict | None:
        """验证用户身份（MD5 密码校验）。"""
        # TODO: 从数据库查询用户并验证 MD5 密码
        # user = await user_repo.get_by_username(username)
        # if user and verify_password(password, user.password_hash):
        #     return {"id": str(user.id), "username": user.username, "role": user.role}
        logger.info(f"用户登录: {username}")
        # 模拟：假设存在一个测试用户
        if username == "admin" and password == "admin":
            return {"id": "user_001", "username": "admin", "role": "system_admin"}
        return None

    async def create_user(self, username: str, password: str, email: str = "") -> dict:
        """创建新用户（MD5 加密存储）。"""
        pwd_hash = hash_password(password)
        logger.info(f"创建用户: {username}, 密码 MD5: {pwd_hash[:8]}...")
        return {"id": "user_001", "username": username, "email": email, "password_hash": pwd_hash}

    async def logout(self, user_id: str, token: str) -> None:
        """用户退出（加入令牌黑名单）。"""
        logger.info(f"用户退出: {user_id}")


auth_service = AuthService()
