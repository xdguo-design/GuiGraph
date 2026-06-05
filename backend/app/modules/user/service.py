"""用户模块服务层。"""

from loguru import logger


class UserService:
    """用户业务逻辑。"""

    async def get_user(self, user_id: str) -> dict | None:
        """获取用户信息。"""
        # TODO: 从数据库查询
        logger.info(f"查询用户: {user_id}")
        return None

    async def update_user(self, user_id: str, data: dict) -> bool:
        """更新用户信息。"""
        logger.info(f"更新用户: {user_id}")
        return True

    async def bind_wechat(self, user_id: str, openid: str, unionid: str) -> bool:
        """绑定微信账号。"""
        logger.info(f"绑定微信: user={user_id}, openid={openid}")
        return True

    async def upload_avatar(self, user_id: str, file_bytes: bytes, filename: str) -> str:
        """上传头像至 MinIO。"""
        # TODO: 上传并返回 URL
        return f"/avatars/{user_id}/{filename}"


user_service = UserService()
