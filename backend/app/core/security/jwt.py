"""JWT 认证工具。"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from app.config.settings import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """生成访问令牌（短期，2 小时）。Token 中携带 sub(用户ID)、username、role。"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES))
    to_encode["exp"] = expire
    to_encode["iat"] = datetime.now(timezone.utc)
    to_encode["type"] = "access"
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """生成刷新令牌（长期，7 天）。"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    to_encode["exp"] = expire
    to_encode["iat"] = datetime.now(timezone.utc)
    to_encode["type"] = "refresh"
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """解码并验证令牌（不校验过期）。"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": False},
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> Optional[dict]:
    """验证令牌（校验过期）并返回完整载荷。"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") in ("access", "refresh"):
            return payload
        return None
    except JWTError:
        return None


def get_token_payload(token: str) -> Optional[dict]:
    """获取令牌完整载荷（含 role、username 等）。"""
    return decode_token(token)
