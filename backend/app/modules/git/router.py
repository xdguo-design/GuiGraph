"""Git 集成模块路由。"""

from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response, PageResponse
from app.modules.git.schemas import GitRepoCreate, MergeRequest
from app.modules.git.service import git_service
from app.modules.user.models import SysUser

router = APIRouter()


@router.get("/repos")
async def list_repos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取用户可访问的 Git 仓库列表。"""
    items, total = await git_service.list_repos(
        db, page=page, page_size=page_size, user_id=current_user.id
    )
    return Response.ok(PageResponse.paginate(items=items, total=total, page=page, page_size=page_size))


@router.post("/repos")
async def create_repo(
    body: GitRepoCreate,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加 Git 仓库。"""
    repo = await git_service.create_repo(
        db,
        team_id=int(body.team_id),
        name=body.name,
        url=body.url,
        auth_type=body.auth_type.value if hasattr(body.auth_type, "value") else str(body.auth_type),
        auth_token=body.auth_token,
        ssh_key=body.ssh_key,
        created_by=current_user.id,
    )
    return Response.ok(repo)


@router.get("/repos/{repo_id}")
async def get_repo(
    repo_id: int,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取单个 Git 仓库详情。"""
    repo = await git_service.get_repo(db, repo_id)
    if not repo:
        return Response.fail(message="仓库不存在", code="NOT_FOUND")
    return Response.ok(repo)


@router.put("/repos/{repo_id}")
async def update_repo(
    repo_id: int,
    body: GitRepoCreate,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新 Git 仓库信息。"""
    repo = await git_service.update_repo(
        db,
        repo_id=repo_id,
        name=body.name,
        url=body.url,
        auth_type=body.auth_type.value if hasattr(body.auth_type, "value") else str(body.auth_type),
        auth_token=body.auth_token,
        ssh_key=body.ssh_key,
    )
    if not repo:
        return Response.fail(message="仓库不存在", code="NOT_FOUND")
    return Response.ok(repo)


@router.delete("/repos/{repo_id}")
async def delete_repo(
    repo_id: int,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除 Git 仓库。"""
    success = await git_service.delete_repo(db, repo_id)
    if not success:
        return Response.fail(message="仓库不存在", code="NOT_FOUND")
    return Response.ok({"message": "删除成功"})


@router.get("/repos/{repo_id}/branches")
async def list_branches(
    repo_id: int,
    current_user: SysUser = Depends(get_current_user),
):
    """获取分支列表。"""
    branches = await git_service.get_branches(str(repo_id))
    return Response.ok({"branches": branches, "repo_id": str(repo_id)})


@router.post("/repos/{repo_id}/auth")
async def auth_repo(
    repo_id: int,
    user_id: int = Body(..., embed=True),
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """为用户授权 Git 仓库。"""
    success = await git_service.auth_repo(
        db, repo_id=repo_id, user_id=user_id, granted_by=current_user.id
    )
    if not success:
        return Response.fail(message="仓库不存在", code="NOT_FOUND")
    return Response.ok({"message": "授权成功"})


@router.delete("/repos/{repo_id}/auth/{user_id}")
async def revoke_auth(
    repo_id: int,
    user_id: int,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """撤销用户授权。"""
    success = await git_service.revoke_auth(db, repo_id=repo_id, user_id=user_id)
    if not success:
        return Response.fail(message="授权记录不存在", code="NOT_FOUND")
    return Response.ok({"message": "撤销成功"})


@router.post("/repos/test")
async def test_repo(
    body: GitRepoCreate,
    current_user: SysUser = Depends(get_current_user),
):
    """测试 Git 仓库连接。"""
    result = await git_service.test_repo_connection(
        url=body.url,
        auth_type=body.auth_type.value if hasattr(body.auth_type, "value") else str(body.auth_type),
        auth_token=body.auth_token,
        ssh_key=body.ssh_key,
    )
    return Response.ok(result)


@router.post("/merge")
async def merge_branches(
    body: MergeRequest,
    current_user: SysUser = Depends(get_current_user),
):
    """执行 Git 合并。"""
    result = await git_service.merge_branches(
        repo_id=body.repo_id,
        source=body.source_branch,
        target=body.target_branch,
        user_id=current_user.id,
    )
    return Response.ok(result)


@router.get("/merge/logs")
async def get_merge_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取合并日志。"""
    items, total = await git_service.get_merge_logs(db, page=page, page_size=page_size)
    return Response.ok(PageResponse.paginate(items=items, total=total, page=page, page_size=page_size))
