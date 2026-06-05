"""升级日志模块 ORM 模型。"""

from sqlalchemy import String, Integer, DateTime, JSON, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base, TimestampMixin
from app.shared.enums import UpgradeType, UpgradeStatus


class SysUpgradeLog(Base, TimestampMixin):
    """升级日志表。"""
    __tablename__ = "sys_upgrade_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    version_from: Mapped[str] = mapped_column(String(50), nullable=False, comment="升级前版本")
    version_to: Mapped[str] = mapped_column(String(50), nullable=False, comment="升级后版本")
    upgrade_type: Mapped[UpgradeType] = mapped_column(Enum(UpgradeType), nullable=False, comment="升级类型")
    status: Mapped[UpgradeStatus] = mapped_column(Enum(UpgradeStatus), default=UpgradeStatus.PENDING, comment="状态")
    start_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, comment="升级开始时间")
    end_time: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True, comment="升级结束时间")
    duration_sec: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="升级耗时（秒）")
    operator_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="操作人 ID")
    change_items: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, comment="关联的变更条目 ID 数组")
    git_commits: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, comment="关联的 Git Commit 列表")
    jenkins_builds: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, comment="关联的 Jenkins 构建 ID 列表")
    log_details: Mapped[str | None] = mapped_column(Text, nullable=True, comment="升级详细日志")
    error_msg: Mapped[str | None] = mapped_column(Text, nullable=True, comment="错误信息（失败时）")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "version_from": self.version_from,
            "version_to": self.version_to,
            "upgrade_type": self.upgrade_type.value,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_sec": self.duration_sec,
            "operator_id": str(self.operator_id),
            "change_items": self.change_items,
            "git_commits": self.git_commits,
            "jenkins_builds": self.jenkins_builds,
            "log_details": self.log_details,
            "error_msg": self.error_msg,
        }
