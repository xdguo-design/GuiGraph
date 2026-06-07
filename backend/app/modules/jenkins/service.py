"""Jenkins 集成模块服务层。"""

import uuid
from datetime import datetime, timezone
from typing import Optional

import httpx
from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.modules.jenkins.models import SysJenkinsInstance, BizJenkinsJob


class JenkinsService:
    """Jenkins 业务逻辑。"""

    def __init__(self):
        self.default_url = settings.JENKINS_DEFAULT_URL
        self.default_token = settings.JENKINS_DEFAULT_TOKEN
        # 内存构建记录: {build_id: {...}}
        # 当 Jenkins 不可达或无 db 参数时回退到 mock 模式，
        # get_build_status / get_build_log / stop_build 通过此记录获取上下文
        self._builds: dict[str, dict] = {}

    # ------------------------------------------------------------------
    # CRUD: 实例管理
    # ------------------------------------------------------------------

    async def list_instances(
        self, db: AsyncSession, page: int = 1, page_size: int = 20
    ) -> dict:
        """查询 Jenkins 实例列表（分页）。"""
        total_q = select(func.count(SysJenkinsInstance.id))
        total = (await db.execute(total_q)).scalar() or 0

        q = (
            select(SysJenkinsInstance)
            .order_by(SysJenkinsInstance.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await db.execute(q)).scalars().all()

        items = [r.to_dict() for r in rows]
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def get_instance(self, db: AsyncSession, instance_id: int) -> dict | None:
        """获取 Jenkins 实例详情。"""
        row = await db.get(SysJenkinsInstance, instance_id)
        return row.to_dict() if row else None

    async def create_instance(self, db: AsyncSession, data: dict) -> dict:
        """创建 Jenkins 实例。"""
        record = SysJenkinsInstance(**data)
        db.add(record)
        await db.flush()
        logger.info(f"创建 Jenkins 实例: {data.get('name')}")
        return record.to_dict()

    async def update_instance(
        self, db: AsyncSession, instance_id: int, data: dict
    ) -> dict | None:
        """更新 Jenkins 实例。"""
        record = await db.get(SysJenkinsInstance, instance_id)
        if not record:
            return None
        for k, v in data.items():
            if hasattr(record, k) and k != "id":
                setattr(record, k, v)
        await db.flush()
        logger.info(f"更新 Jenkins 实例: {instance_id}")
        return record.to_dict()

    async def delete_instance(self, db: AsyncSession, instance_id: int) -> bool:
        """删除 Jenkins 实例。"""
        record = await db.get(SysJenkinsInstance, instance_id)
        if not record:
            return False
        await db.delete(record)
        logger.info(f"删除 Jenkins 实例: {instance_id}")
        return True

    # ------------------------------------------------------------------
    # 构建管理
    # ------------------------------------------------------------------

    async def trigger_build(
        self,
        job_name: str,
        params: dict | None = None,
        db: AsyncSession | None = None,
    ) -> dict:
        """触发 Jenkins 构建。

        当提供 ``db`` 时会从数据库查询 Jenkins 实例和 Job 信息，
        通过 httpx 调用 Jenkins REST API 触发构建。
        若 Jenkins 不可达、数据库未配置、或未提供 ``db`` 则回退到 mock 模式。
        """
        build_id = f"build_{uuid.uuid4().hex[:8]}"

        # --- 尝试真实调用 ---
        if db is not None:
            try:
                job_q = select(BizJenkinsJob).where(BizJenkinsJob.job_name == job_name)
                job_row = (await db.execute(job_q)).scalars().first()
                if job_row:
                    instance = await db.get(
                        SysJenkinsInstance, job_row.jenkins_instance_id
                    )
                    if instance:
                        result = await self._call_jenkins_trigger(
                            instance=instance,
                            job=job_row,
                            params=params,
                        )

                        self._builds[build_id] = {
                            "build_id": build_id,
                            "job_name": job_name,
                            "instance_url": instance.url,
                            "instance_auth_token": instance.auth_token,
                            "instance_auth_type": instance.auth_type.value
                            if instance.auth_type
                            else "token",
                            "job_url": job_row.job_url,
                            "jenkins_build_number": result.get("build_number"),
                            "queue_url": result.get("queue_url"),
                            "status": "running",
                            "params": params,
                            "mock": False,
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        }

                        logger.info(
                            f"Jenkins 构建已触发: job={job_name}, "
                            f"instance={instance.name}, build_id={build_id}"
                        )
                        return {"build_id": build_id, "status": "running"}
                else:
                    logger.warning(f"数据库未找到 Job 记录: {job_name}")
            except Exception as e:
                logger.warning(f"Jenkins API 调用失败，回退到 mock 模式: {e}")

        # --- Mock 兜底 ---
        self._builds[build_id] = {
            "build_id": build_id,
            "job_name": job_name,
            "status": "running",
            "params": params,
            "mock": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        logger.info(f"Mock 触发构建: job={job_name}, build_id={build_id}")
        return {"build_id": build_id, "status": "running"}

    async def get_build_status(self, build_id: str) -> dict:
        """获取构建状态。

        优先从内存构建记录匹配的 Jenkins 实例查询实时状态，
        无记录或实例不可达时返回 mock 数据。
        """
        build = self._builds.get(build_id)
        if not build:
            logger.warning(f"未找到构建记录: {build_id}")
            return {"status": "unknown", "progress": 0}

        # Mock 模式
        if build.get("mock"):
            return {"status": "running", "progress": 50}

        # 查询 Jenkins 实时状态
        try:
            instance_url = build.get("instance_url", "")
            job_url = build.get("job_url", "").rstrip("/")
            jenkins_build_number = build.get("jenkins_build_number")

            # 如果还没有 build number，可能仍在队列中
            if jenkins_build_number is None:
                queue_url = build.get("queue_url", "")
                if queue_url:
                    info = await self._call_jenkins_api(
                        queue_url.rstrip("/") + "/api/json",
                        instance_url=instance_url,
                        auth_token=build.get("instance_auth_token"),
                        auth_type=build.get("instance_auth_type"),
                    )
                    if info and info.get("executable"):
                        build_number = info["executable"].get("number")
                        build["jenkins_build_number"] = build_number
                        jenkins_build_number = build_number
                    else:
                        return {"status": "queued", "progress": 0}
                else:
                    return {"status": "queued", "progress": 0}

            build_api_url = f"{job_url}/{jenkins_build_number}/api/json"
            info = await self._call_jenkins_api(
                build_api_url,
                instance_url=instance_url,
                auth_token=build.get("instance_auth_token"),
                auth_type=build.get("instance_auth_type"),
            )

            if info:
                if info.get("building"):
                    return {"status": "running", "progress": 50}
                result = info.get("result")
                if result == "SUCCESS":
                    return {"status": "success", "progress": 100}
                if result == "FAILURE":
                    return {"status": "failed", "progress": 100}
                if result == "ABORTED":
                    return {"status": "stopped", "progress": 0}
                if result:
                    return {"status": result.lower(), "progress": 100}

            # API 返回空 —— 保守返回 running
            return {"status": "running", "progress": 50}

        except Exception as e:
            logger.warning(f"查询 Jenkins 构建状态失败: {e}")
            return {"status": build.get("status", "running"), "progress": 50}

    async def get_build_log(self, build_id: str) -> str:
        """获取构建日志。

        优先从 Jenkins 实例获取实时日志文本，
        回退时返回 mock 日志内容。
        """
        build = self._builds.get(build_id)
        if not build:
            logger.warning(f"未找到构建记录: {build_id}")
            return ""

        # Mock 模式
        if build.get("mock"):
            now = datetime.now(timezone.utc).isoformat()
            return (
                f"[{now}] Mock build started for {build.get('job_name', 'unknown')}\n"
                f"[{now}] Build {build_id} in progress...\n"
                f"[{now}] Mock build completed."
            )

        instance_url = build.get("instance_url", "")
        job_url = build.get("job_url", "").rstrip("/")
        jenkins_build_number = build.get("jenkins_build_number")

        if jenkins_build_number is None:
            return ""

        try:
            console_url = f"{job_url}/{jenkins_build_number}/consoleText"
            auth_token = build.get("instance_auth_token") or self.default_token

            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                resp = await client.get(
                    console_url,
                    auth=self._build_auth(auth_token, build.get("instance_auth_type")),
                )
                resp.raise_for_status()
                return resp.text
        except Exception as e:
            logger.warning(f"获取 Jenkins 构建日志失败: {e}")
            return f"[{datetime.now(timezone.utc).isoformat()}] Failed to fetch log: {e}"

    async def stop_build(self, build_id: str) -> bool:
        """停止构建。

        优先调用 Jenkins API 发送停止请求，
        回退时仅更新内存状态并返回 True。
        """
        build = self._builds.get(build_id)
        if not build:
            logger.warning(f"未找到构建记录: {build_id}")
            return False

        # Mock 模式
        if build.get("mock"):
            build["status"] = "stopped"
            logger.info(f"Mock 停止构建: {build_id}")
            return True

        instance_url = build.get("instance_url", "")
        job_url = build.get("job_url", "").rstrip("/")
        jenkins_build_number = build.get("jenkins_build_number")

        if jenkins_build_number is None:
            return False

        try:
            stop_url = f"{job_url}/{jenkins_build_number}/stop"
            auth_token = build.get("instance_auth_token") or self.default_token

            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    stop_url,
                    auth=self._build_auth(auth_token, build.get("instance_auth_type")),
                )
                resp.raise_for_status()

            build["status"] = "stopped"
            logger.info(f"Jenkins 构建已停止: {build_id}")
            return True
        except Exception as e:
            logger.warning(f"停止 Jenkins 构建失败，标记为已停止: {e}")
            build["status"] = "stopped"
            return True

    # ------------------------------------------------------------------
    # Jenkins REST API 底层调用
    # ------------------------------------------------------------------

    async def _call_jenkins_trigger(
        self,
        instance: SysJenkinsInstance,
        job: BizJenkinsJob,
        params: dict | None = None,
    ) -> dict:
        """调用 Jenkins REST API 触发构建，返回 queue 信息。"""
        job_url = job.job_url.rstrip("/")
        # 带参数的构建 vs 无参数构建
        api_url = f"{job_url}/buildWithParameters" if params else f"{job_url}/build"

        logger.info(f"调用 Jenkins API: {api_url}")

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
            resp = await client.post(
                api_url,
                params=params,
                auth=self._build_auth(
                    instance.auth_token, instance.auth_type.value if instance.auth_type else None
                ),
            )
            # Jenkins 触发成功通常返回 201 (Created)
            if resp.status_code not in (200, 201, 202):
                resp.raise_for_status()

        queue_url = resp.headers.get("Location", "")
        build_number: Optional[int] = None

        # 尝试解析 queue 响应中的 build number（非阻塞，失败不影响）
        if queue_url:
            try:
                qid = queue_url.rstrip("/").rsplit("/", 1)[-1]
                if qid.isdigit():
                    build_number = int(qid)
            except (ValueError, IndexError):
                pass

        return {"queue_url": queue_url, "build_number": build_number}

    async def _call_jenkins_api(
        self,
        url: str,
        instance_url: str = "",
        auth_token: str | None = None,
        auth_type: str | None = None,
    ) -> dict | None:
        """通用 Jenkins API GET 请求，返回 JSON 数据。

        失败时返回 None 而非抛出异常，便于上游优雅降级。
        """
        token = auth_token or self.default_token
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                resp = await client.get(
                    url,
                    auth=self._build_auth(token, auth_type),
                )
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPStatusError as e:
            logger.warning(
                f"Jenkins API HTTP 错误: url={url}, status={e.response.status_code}"
            )
        except httpx.RequestError as e:
            logger.warning(f"Jenkins API 请求失败: url={url}, error={e}")
        except Exception as e:
            logger.warning(f"Jenkins API 未知错误: url={url}, error={e}")
        return None

    # ------------------------------------------------------------------
    # 认证工具
    # ------------------------------------------------------------------

    @staticmethod
    def _build_auth(
        token: str | None, auth_type: str | None = None
    ) -> httpx.BasicAuth:
        """根据认证类型构造 httpx BasicAuth。"""
        t = (auth_type or "token").lower()
        if t == "basic":
            parts = (token or ":").split(":", 1)
            username = parts[0] or "admin"
            password = parts[1] if len(parts) > 1 else ""
            return httpx.BasicAuth(username=username, password=password)

        # token 模式：将 token 作为密码，用户名为 admin
        return httpx.BasicAuth(username="admin", password=token or "")


jenkins_service = JenkinsService()
