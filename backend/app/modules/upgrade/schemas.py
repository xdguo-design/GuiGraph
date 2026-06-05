"""升级日志 Schema 定义。"""

from typing import Optional

from pydantic import BaseModel, Field


class UpgradeLogResponse(BaseModel):
    """升级日志响应。"""
    id: str
    version_from: str
    version_to: str
    upgrade_type: str
    status: str
    start_time: str
    end_time: str
    duration_sec: int
    operator_id: str
    change_items: Optional[list[str]]
    git_commits: Optional[list[str]]
    jenkins_builds: Optional[list[str]]
    error_msg: Optional[str]
