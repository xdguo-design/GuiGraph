"""通用工具函数。"""

import hashlib
import uuid
from datetime import datetime


def generate_uuid() -> str:
    """生成 UUID。"""
    return str(uuid.uuid4())


def generate_short_uuid() -> str:
    """生成短 UUID（8 字符）。"""
    return uuid.uuid4().hex[:8]


def md5_hash(data: str) -> str:
    """计算 MD5 哈希。"""
    return hashlib.md5(data.encode("utf-8")).hexdigest()


def parse_datetime(dt_str: str) -> datetime | None:
    """解析多种格式的日期字符串。"""
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    return None


def safe_get(data: dict, *keys, default=None):
    """安全地嵌套获取字典值。"""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data
