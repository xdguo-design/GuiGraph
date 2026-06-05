"""Git 集成模块服务层。"""

from loguru import logger


class GitService:
    """Git 业务逻辑。"""

    async def list_repos(self, user_id: str) -> list[dict]:
        """获取用户可访问的仓库。"""
        logger.info(f"查询仓库: {user_id}")
        return []

    async def get_branches(self, repo_id: str) -> list[dict]:
        """获取仓库分支列表。"""
        logger.info(f"查询分支: {repo_id}")
        return []

    async def merge_branches(
        self,
        repo_id: str,
        source: str,
        target: str,
        user_id: str,
    ) -> dict:
        """执行合并。"""
        logger.info(f"合并分支: {source} -> {target}, repo={repo_id}, by={user_id}")
        return {"success": True, "message": "合并成功"}


git_service = GitService()
