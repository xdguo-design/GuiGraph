"""Jenkins 集成模块 ORM 模型。"""

from sqlalchemy import String, Integer, Text, JSON, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, TimestampMixin
from app.shared.enums import AuthType


class SysJenkinsInstance(Base, TimestampMixin):
    """Jenkins 实例表。"""
    __tablename__ = "sys_jenkins_instance"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="实例名称")
    url: Mapped[str] = mapped_column(String(500), nullable=False, comment="Jenkins URL")
    auth_type: Mapped[AuthType] = mapped_column(Enum(AuthType), nullable=False, comment="认证类型")
    auth_token: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="Token（加密存储）")
    created_by: Mapped[int] = mapped_column(Integer, nullable=False, comment="创建人 ID")

    jobs = relationship("BizJenkinsJob", back_populates="instance", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "url": self.url,
            "auth_type": self.auth_type.value,
            "created_by": str(self.created_by),
        }


class BizJenkinsJob(Base, TimestampMixin):
    """Jenkins Job 模板表。"""
    __tablename__ = "biz_jenkins_job"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    repo_id: Mapped[int] = mapped_column(Integer, ForeignKey("biz_git_repo.id"), nullable=False, comment="关联的 Git 仓库 ID")
    jenkins_instance_id: Mapped[int] = mapped_column(Integer, ForeignKey("sys_jenkins_instance.id"), nullable=False, comment="Jenkins 实例 ID")
    job_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="Job 全名")
    job_url: Mapped[str] = mapped_column(String(500), nullable=False, comment="Job URL")
    trigger_params: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="触发参数模板")

    repo = relationship("BizGitRepo", back_populates="jenkins_jobs")
    instance = relationship("SysJenkinsInstance", back_populates="jobs")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "repo_id": str(self.repo_id),
            "jenkins_instance_id": str(self.jenkins_instance_id),
            "job_name": self.job_name,
            "job_url": self.job_url,
            "trigger_params": self.trigger_params,
        }
