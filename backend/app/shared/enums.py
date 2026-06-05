"""全局枚举定义。"""

from enum import Enum


class ChangeType(str, Enum):
    """变更类型。"""
    DB = "db"
    API = "api"
    CONFIG = "config"
    CODE = "code"
    INFRA = "infra"


class ChangeReason(str, Enum):
    """变更原因。"""
    REQUIREMENT = "requirement"
    BUG_FIX = "bug_fix"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    TECH_DEBT = "tech_debt"
    OTHER = "other"


class ChangeStatus(str, Enum):
    """变更状态。"""
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    RELEASED = "released"
    ROLLED_BACK = "rolled_back"


class LoginMethod(str, Enum):
    """登录方式。"""
    PASSWORD = "password"
    WECHAT = "wechat"
    BOTH = "both"


class UserStatus(str, Enum):
    """用户状态。"""
    ACTIVE = "active"
    DISABLED = "disabled"
    LOCKED = "locked"


class AuthType(str, Enum):
    """认证类型（Git/Jenkins/MinIO）。"""
    TOKEN = "token"
    SSH = "ssh"
    BASIC = "basic"


class FileAttachmentType(str, Enum):
    """附件类型。"""
    IMAGE = "image"
    DOCUMENT = "document"


class BizFileType(str, Enum):
    """业务类型（附件表）。"""
    CHANGE = "change"
    VERSION = "version"
    INCIDENT = "incident"
    USER_AVATAR = "user_avatar"


class UpgradeType(str, Enum):
    """升级类型。"""
    FULL = "full"
    PARTIAL = "partial"
    ROLLBACK = "rollback"


class UpgradeStatus(str, Enum):
    """升级状态。"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
