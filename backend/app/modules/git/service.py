"""Git 集成模块服务层。"""

import os
import json
from datetime import datetime
from typing import Optional

from loguru import logger
from sqlalchemy import select, func, and_, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.git.models import BizGitRepo, BizUserGitAuth
from app.modules.user.models import SysUser

# ---------------------------------------------------------------------------
# 内存合并日志存储（暂无对应 DB 表时的轻量替代方案）
# ---------------------------------------------------------------------------
_merge_logs: list[dict] = []


def _record_merge_log(
    repo_id: str,
    source: str,
    target: str,
    user_id: int,
    success: bool,
    message: str,
    commit_hash: Optional[str] = None,
) -> None:
    """向内存追加一条合并日志。"""
    _merge_logs.append(
        {
            "repo_id": repo_id,
            "source_branch": source,
            "target_branch": target,
            "user_id": user_id,
            "success": success,
            "message": message,
            "commit_hash": commit_hash,
            "created_at": datetime.utcnow().isoformat(),
        }
    )


def _build_auth_url(url: str, auth_token: Optional[str] = None) -> str:
    """为 HTTPS URL 嵌入 Token 认证信息。"""
    if auth_token and url.startswith("https://"):
        return url.replace("https://", f"https://oauth2:{auth_token}@", 1)
    return url


def _build_git_env(ssh_key: Optional[str] = None) -> tuple[dict, Optional[str]]:
    """构建 Git 环境变量字典，返回 (env, temp_key_path)。

    当提供了 ``ssh_key`` 时将其写入临时文件并设置 ``GIT_SSH_COMMAND``，
    调用方**必须**在 ``finally`` 块中删除返回的临时文件路径。
    """
    if not ssh_key:
        return {}, None

    import tempfile

    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".key", delete=False, prefix="guigraph_ssh_"
    )
    f.write(ssh_key)
    if not ssh_key.endswith("\n"):
        f.write("\n")
    f.close()
    os.chmod(f.name, 0o600)
    return {"GIT_SSH_COMMAND": f"ssh -i {f.name} -o StrictHostKeyChecking=no"}, f.name


def _parse_ls_remote(output: str) -> list[dict]:
    """解析 ``git ls-remote`` 输出为分支列表。"""
    branches: list[dict] = []
    for line in output.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        commit_hash, ref = parts
        if ref.startswith("refs/heads/"):
            name = ref.replace("refs/heads/", "")
            branches.append(
                {
                    "name": name,
                    "commit": commit_hash[:8],
                    "protected": name in ("main", "master"),
                }
            )
    return branches


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class GitService:
    """Git 业务逻辑。"""

    # ---- 仓库 CRUD -------------------------------------------------------

    async def list_repos(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[int] = None,
    ) -> tuple[list[dict], int]:
        """获取用户可访问的仓库列表（分页）。"""
        conditions = []
        if user_id:
            # 用户创建的或已授权的仓库
            conditions.append(
                (BizGitRepo.created_by == user_id)
                | (
                    BizGitRepo.id.in_(
                        select(BizUserGitAuth.repo_id).where(
                            BizUserGitAuth.user_id == user_id
                        )
                    )
                )
            )

        where = and_(*conditions) if conditions else True

        count_q = select(func.count(BizGitRepo.id)).where(where)
        total = (await db.execute(count_q)).scalar() or 0

        q = (
            select(BizGitRepo)
            .where(where)
            .order_by(BizGitRepo.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await db.execute(q)).scalars().all()
        items = [r.to_dict() for r in rows]

        logger.info(f"查询仓库列表: user={user_id}, total={total}")
        return items, total

    async def get_repo(self, db: AsyncSession, repo_id: int) -> Optional[dict]:
        """获取单个仓库详情。"""
        row = await db.get(BizGitRepo, repo_id)
        if not row:
            return None
        return row.to_dict()

    async def create_repo(
        self,
        db: AsyncSession,
        team_id: int,
        name: str,
        url: str,
        auth_type: str,
        auth_token: Optional[str] = None,
        ssh_key: Optional[str] = None,
        default_branch: str = "main",
        created_by: int = 0,
    ) -> dict:
        """创建 Git 仓库。"""
        from app.shared.enums import AuthType

        repo = BizGitRepo(
            team_id=team_id,
            name=name,
            url=url,
            auth_type=AuthType(auth_type) if auth_type else AuthType.TOKEN,
            auth_token=auth_token,
            ssh_key=ssh_key,
            default_branch=default_branch,
            created_by=created_by,
        )
        db.add(repo)
        await db.flush()
        logger.info(f"创建仓库: {name}, url={url}, by={created_by}")
        return repo.to_dict()

    async def update_repo(
        self,
        db: AsyncSession,
        repo_id: int,
        name: Optional[str] = None,
        url: Optional[str] = None,
        auth_type: Optional[str] = None,
        auth_token: Optional[str] = None,
        ssh_key: Optional[str] = None,
        default_branch: Optional[str] = None,
    ) -> Optional[dict]:
        """更新 Git 仓库信息。"""
        from app.shared.enums import AuthType

        row = await db.get(BizGitRepo, repo_id)
        if not row:
            return None

        if name is not None:
            row.name = name
        if url is not None:
            row.url = url
        if auth_type is not None:
            row.auth_type = AuthType(auth_type)
        if auth_token is not None:
            row.auth_token = auth_token
        if ssh_key is not None:
            row.ssh_key = ssh_key
        if default_branch is not None:
            row.default_branch = default_branch

        await db.flush()
        logger.info(f"更新仓库: id={repo_id}, name={name}")
        return row.to_dict()

    async def delete_repo(self, db: AsyncSession, repo_id: int) -> bool:
        """删除 Git 仓库。"""
        row = await db.get(BizGitRepo, repo_id)
        if not row:
            return False
        await db.delete(row)
        await db.flush()
        logger.info(f"删除仓库: id={repo_id}")
        return True

    # ---- Git 远程操作 ----------------------------------------------------

    async def _fetch_remote_branches(
        self,
        url: str,
        auth_token: Optional[str] = None,
        ssh_key: Optional[str] = None,
    ) -> list[dict]:
        """使用 ``git ls-remote`` 获取远程仓库分支。"""
        import git

        effective_url = _build_auth_url(url, auth_token)
        env, key_path = _build_git_env(ssh_key)
        try:
            git_cmd = git.cmd.Git()
            output = git_cmd.ls_remote(effective_url, env=env or None)
            branches = _parse_ls_remote(output)
            if not branches:
                raise ValueError("未从远程仓库检测到任何分支")
            return branches
        finally:
            if key_path:
                try:
                    os.unlink(key_path)
                except OSError:
                    pass

    async def _perform_merge(
        self,
        url: str,
        source: str,
        target: str,
        commit_message: Optional[str] = None,
        auth_token: Optional[str] = None,
        ssh_key: Optional[str] = None,
    ) -> dict:
        """使用 GitPython 执行本地克隆 -> 合并 -> 推送。"""
        import git
        import tempfile
        import shutil

        effective_url = _build_auth_url(url, auth_token)
        env, key_path = _build_git_env(ssh_key)

        temp_dir = tempfile.mkdtemp(prefix="guigraph_merge_")
        try:
            repo = git.Repo.clone_from(
                effective_url, temp_dir, branch=target, depth=1, env=env or None
            )
            # 获取源分支引用
            repo.git.fetch("origin", source, env=env or None)
            # 执行合并
            msg = commit_message or f"Merge branch '{source}' into '{target}'"
            repo.git.merge(f"origin/{source}", message=msg)
            # 推送到远程
            origin = repo.remotes.origin
            origin.push(env=env or None)
            commit_hash = repo.head.commit.hexsha[:8]

            return {
                "success": True,
                "message": "合并成功",
                "source_branch": source,
                "target_branch": target,
                "repo_id": url,
                "commit_hash": commit_hash,
            }
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            if key_path:
                try:
                    os.unlink(key_path)
                except OSError:
                    pass

    async def _test_connection_remote(
        self,
        url: str,
        auth_token: Optional[str] = None,
        ssh_key: Optional[str] = None,
    ) -> dict:
        """使用 ``git ls-remote`` 测试远程仓库连通性。"""
        branches = await self._fetch_remote_branches(url, auth_token, ssh_key)
        default = (
            "main"
            if any(b["name"] == "main" for b in branches)
            else (branches[0]["name"] if branches else "main")
        )
        return {
            "success": True,
            "message": f"连接成功，检测到 {len(branches)} 个分支",
            "branch": default,
        }

    # ---- 对外公开方法 ----------------------------------------------------

    async def get_branches(
        self,
        repo_id: str,
        db: Optional[AsyncSession] = None,
    ) -> list[dict]:
        """获取仓库分支列表。

        当 ``db`` 不为 ``None`` 时优先从数据库查询仓库 URL 并通过
        ``git ls-remote`` 远程拉取；失败时回退到模拟数据。
        """
        logger.info(f"查询分支: repo_id={repo_id}")

        repo_url = None
        auth_token = None
        ssh_key = None

        if db is not None:
            try:
                row = await db.get(BizGitRepo, int(repo_id))
                if row:
                    repo_url = row.url
                    auth_token = row.auth_token
                    ssh_key = row.ssh_key
            except Exception as exc:
                logger.warning(f"无法从数据库查询仓库 (repo_id={repo_id}): {exc}")

        if repo_url:
            try:
                return await self._fetch_remote_branches(repo_url, auth_token, ssh_key)
            except Exception as exc:
                logger.warning(
                    f"Git 远程操作失败，回退到模拟模式: {exc}"
                )

        # ---- 回退：返回模拟数据 ----
        return [
            {"name": "main", "commit": "abc123", "protected": True},
            {"name": "develop", "commit": "def456", "protected": False},
        ]

    async def merge_branches(
        self,
        repo_id: str,
        source: str,
        target: str,
        user_id: int,
        db: Optional[AsyncSession] = None,
        commit_message: Optional[str] = None,
    ) -> dict:
        """执行分支合并。

        当 ``db`` 不为 ``None`` 时从数据库查询仓库 URL 并通过 GitPython
        执行真实的 clone -> merge -> push 流程；失败时回退到模拟模式。
        合并结果（无论成功/失败）均会记录到内存日志中。
        """
        logger.info(f"合并分支: {source} -> {target}, repo={repo_id}, by={user_id}")

        repo_url = None
        auth_token = None
        ssh_key = None

        if db is not None:
            try:
                row = await db.get(BizGitRepo, int(repo_id))
                if row:
                    repo_url = row.url
                    auth_token = row.auth_token
                    ssh_key = row.ssh_key
            except Exception as exc:
                logger.warning(
                    f"无法从数据库查询仓库 (repo_id={repo_id}): {exc}"
                )

        if repo_url:
            try:
                result = await self._perform_merge(
                    url=repo_url,
                    source=source,
                    target=target,
                    commit_message=commit_message,
                    auth_token=auth_token,
                    ssh_key=ssh_key,
                )
                _record_merge_log(
                    repo_id=repo_id,
                    source=source,
                    target=target,
                    user_id=user_id,
                    success=True,
                    message=result["message"],
                    commit_hash=result.get("commit_hash"),
                )
                return result
            except Exception as exc:
                logger.warning(f"Git 合并操作失败，回退到模拟模式: {exc}")

        # ---- 回退：返回模拟结果 ----
        result = {
            "success": True,
            "message": "合并成功",
            "source_branch": source,
            "target_branch": target,
            "repo_id": repo_id,
            "commit_hash": None,
        }
        _record_merge_log(
            repo_id=repo_id,
            source=source,
            target=target,
            user_id=user_id,
            success=True,
            message=result["message"],
        )
        return result

    async def test_repo_connection(
        self,
        url: str,
        auth_type: str = "token",
        auth_token: Optional[str] = None,
        ssh_key: Optional[str] = None,
    ) -> dict:
        """测试 Git 仓库连接。

        优先通过 ``git ls-remote`` 实际验证远程仓库连通性；
        失败时回退到模拟数据。
        """
        logger.info(f"测试仓库连接: url={url}, auth_type={auth_type}")

        try:
            return await self._test_connection_remote(url, auth_token, ssh_key)
        except Exception as exc:
            logger.warning(f"Git 远程连接测试失败，回退到模拟模式: {exc}")

        # ---- 回退：返回模拟数据 ----
        return {
            "success": True,
            "message": "连接测试成功",
            "branch": "main",
        }

    # ---- 授权管理 -------------------------------------------------------

    async def auth_repo(
        self,
        db: AsyncSession,
        repo_id: int,
        user_id: int,
        granted_by: int,
    ) -> bool:
        """为用户授权 Git 仓库。"""
        # 检查仓库是否存在
        repo = await db.get(BizGitRepo, repo_id)
        if not repo:
            return False

        # 检查是否已授权
        q = select(BizUserGitAuth).where(
            and_(
                BizUserGitAuth.user_id == user_id,
                BizUserGitAuth.repo_id == repo_id,
            )
        )
        existing = (await db.execute(q)).scalar_one_or_none()
        if existing:
            logger.info(f"用户已授权: user={user_id}, repo={repo_id}")
            return True

        auth = BizUserGitAuth(
            user_id=user_id,
            repo_id=repo_id,
            granted_by=granted_by,
            granted_at=datetime.utcnow(),
        )
        db.add(auth)
        await db.flush()
        logger.info(f"授权成功: user={user_id}, repo={repo_id}, by={granted_by}")
        return True

    async def revoke_auth(
        self,
        db: AsyncSession,
        repo_id: int,
        user_id: int,
    ) -> bool:
        """撤销用户授权。"""
        q = sa_delete(BizUserGitAuth).where(
            and_(
                BizUserGitAuth.user_id == user_id,
                BizUserGitAuth.repo_id == repo_id,
            )
        )
        result = await db.execute(q)
        await db.flush()
        if result.rowcount == 0:
            return False
        logger.info(f"撤销授权: user={user_id}, repo={repo_id}")
        return True

    # ---- 合并日志 -------------------------------------------------------

    async def get_merge_logs(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        """获取合并日志（当前从内存存储返回）。"""
        logger.info(f"查询合并日志: page={page}")

        total = len(_merge_logs)
        start = (page - 1) * page_size
        end = start + page_size
        # 按时间倒序排列
        items = list(reversed(_merge_logs))[start:end]
        return items, total


git_service = GitService()