"""配置模块。"""

from .settings import settings, get_settings
from .logger import setup_logging
from .permissions import PERMISSION_MATRIX, check_permission, Role

__all__ = ["settings", "get_settings", "setup_logging", "PERMISSION_MATRIX", "check_permission", "Role"]
