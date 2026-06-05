"""加密工具（密码 MD5、敏感数据加密）。"""

import hashlib

from cryptography.fernet import Fernet

from app.config.settings import settings


def hash_password(password: str) -> str:
    """使用 MD5 哈希密码。"""
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码（MD5）。"""
    return hash_password(plain_password) == hashed_password


def encrypt_sensitive_data(data: str) -> str:
    """加密敏感数据（如 Token、SSH Key）。"""
    f = Fernet(settings.SECRET_KEY.encode() if len(settings.SECRET_KEY) >= 32 else settings.SECRET_KEY.ljust(32, "x").encode())
    return f.encrypt(data.encode()).decode()


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """解密敏感数据。"""
    f = Fernet(settings.SECRET_KEY.encode() if len(settings.SECRET_KEY) >= 32 else settings.SECRET_KEY.ljust(32, "x").encode())
    return f.decrypt(encrypted_data.encode()).decode()
