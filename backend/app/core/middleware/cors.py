"""CORS 配置（已在 main.py 中配置，此处为补充说明）。"""

from app.config.settings import settings

# 生产环境需根据实际情况调整
ALLOWED_ORIGINS = settings.CORS_ORIGINS
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
ALLOWED_HEADERS = ["Content-Type", "Authorization", "X-Requested-With"]
