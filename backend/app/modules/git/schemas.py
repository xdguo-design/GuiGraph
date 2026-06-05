"""Git 集成模块 Schema 定义。"""

from typing import Optional

from pydantic import BaseModel, Field

from app.shared.enums import AuthType


class GitRepoCreate(BaseModel):
    """创建 Git 仓库。"""
    team_id: str
    name: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., description="Git 仓库地址")
    auth_type: AuthType = Field(AuthType.TOKEN, description="认证类型")
    auth_token: Optional[str] = Field(None, description="Token（加密存储）")
    ssh_key: Optional[str] = Field(None, description="SSH 私钥")


class GitRepoResponse(BaseModel):
    """Git 仓库响应。"""
    id: str
    team_id: str
    name: str
    url: str
    auth_type: str
    default_branch: Optional[str]
    created_by: str


class BranchInfo(BaseModel):
    """分支信息。"""
    name: str
    commit: str
    protected: bool = False


class MergeRequest(BaseModel):
    """合并请求。"""
    repo_id: str
    source_branch: str = Field(..., description="源分支")
    target_branch: str = Field(..., description="目标分支")
    commit_message: Optional[str] = Field(None, description="提交信息")


class MergeResult(BaseModel):
    """合并结果。"""
    success: bool
    message: str
    source_branch: str
    target_branch: str
    repo_id: str
    commit_hash: Optional[str] = None
