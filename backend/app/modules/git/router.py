"""Git 集成模块路由。"""

from fastapi import APIRouter, Depends

from app.core.deps.auth import get_current_user
from app.core.utils.response import Response
from app.modules.git.schemas import (
    GitRepoCreate, GitRepoResponse,
    BranchInfo, MergeRequest,
    MergeResult,
)

router = APIRouter()


@router.get("/repos")
async def list_repos(user_id: str = Depends(get_current_user)):
    """获取用户可访问的 Git 仓库列表。"""
    return Response.ok({"items": [], "total": 0})


@router.post("/repos", response_model=GitRepoResponse)
async def create_repo(
    body: GitRepoCreate,
    user_id: str = Depends(get_current_user),
):
    """添加 Git 仓库。"""
    return Response.ok(GitRepoResponse(
        id="repo_001",
        team_id=body.team_id,
        name=body.name,
        url=body.url,
        auth_type=body.auth_type,
        default_branch="main",
        created_by=user_id,
    ))


@router.get("/repos/{repo_id}/branches")
async def list_branches(repo_id: str, user_id: str = Depends(get_current_user)):
    """获取分支列表。"""
    return Response.ok({
        "branches": [
            BranchInfo(name="main", commit="abc123", protected=True),
            BranchInfo(name="develop", commit="def456", protected=False),
            BranchInfo(name="feature/new", commit="ghi789", protected=False),
        ],
        "repo_id": repo_id,
    })


@router.post("/repos/{repo_id}/auth")
async def auth_repo(
    repo_id: str,
    user_id: str,
    granted_by: str = Depends(get_current_user),
):
    """为用户授权 Git 仓库。"""
    return Response.ok({"message": "授权成功"})


@router.delete("/repos/{repo_id}/auth/{user_id}")
async def revoke_auth(repo_id: str, user_id: str, current_user: str = Depends(get_current_user)):
    """撤销用户授权。"""
    return Response.ok({"message": "撤销成功"})


@router.post("/merge", response_model=MergeResult)
async def merge_branches(
    body: MergeRequest,
    user_id: str = Depends(get_current_user),
):
    """执行 Git 合并。"""
    return Response.ok(MergeResult(
        success=True,
        message="合并成功",
        source_branch=body.source_branch,
        target_branch=body.target_branch,
        repo_id=body.repo_id,
    ))


@router.get("/merge/logs")
async def get_merge_logs(
    page: int = 1,
    page_size: int = 20,
    user_id: str = Depends(get_current_user),
):
    """获取合并日志。"""
    return Response.ok({"items": [], "total": 0, "page": page, "page_size": page_size})
