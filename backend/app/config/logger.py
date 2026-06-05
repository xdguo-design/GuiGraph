"""日志配置（基于 loguru）。"""

import sys
from pathlib import Path

from loguru import logger

from app.config.settings import settings


def setup_logging() -> None:
    """初始化日志系统。"""
    # 移除默认处理器
    logger.remove()

    # 控制台输出（彩色）
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    # 文件输出
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.add(
        settings.LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
    )

    # 异步日志（生产环境建议用队列）
    logger.bind(bind=True)
