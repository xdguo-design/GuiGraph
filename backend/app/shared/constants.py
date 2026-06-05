"""全局常量定义。"""

# ===== 分页 =====
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ===== 文件上传 =====
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_DOC_EXTENSIONS = {".pdf", ".doc", ".docx", ".xlsx", ".xls", ".txt", ".md"}

# ===== JWT =====
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

# ===== 头像 =====
AVATAR_THUMB_SIZE = 100  # 缩略图尺寸

# ===== 默认值 =====
DEFAULT_TEAM_CODE = "default"
DEFAULT_DEPT_CODE = "default"

# ===== 系统标识 =====
SYSTEM_USER_ID = "system"
ANONYMOUS_USER_ID = "anonymous"
