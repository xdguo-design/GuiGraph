"""审计日志服务层。"""

from datetime import datetime
from typing import Optional

from loguru import logger
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models import AuditLog


class AuditService:
    """审计业务逻辑。"""

    async def list_logs(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        user_id: str = "",
        operation: str = "",
        start_time: str = "",
        end_time: str = "",
    ) -> tuple[list[dict], int]:
        """查询审计日志（分页 + 筛选）。"""
        conditions = []
        if user_id:
            conditions.append(AuditLog.user_id == user_id)
        if operation:
            conditions.append(AuditLog.operation.contains(operation))
        if start_time:
            try:
                st = datetime.fromisoformat(start_time)
                conditions.append(AuditLog.timestamp >= st)
            except ValueError:
                pass
        if end_time:
            try:
                et = datetime.fromisoformat(end_time)
                conditions.append(AuditLog.timestamp <= et)
            except ValueError:
                pass

        where = and_(*conditions) if conditions else True

        # 总数
        count_q = select(func.count(AuditLog.id)).where(where)
        total = (await db.execute(count_q)).scalar() or 0

        # 分页
        q = (
            select(AuditLog)
            .where(where)
            .order_by(AuditLog.timestamp.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await db.execute(q)).scalars().all()
        items = [r.to_dict() for r in rows]

        logger.info(f"查询审计日志: user={user_id}, op={operation}, total={total}")
        return items, total

    async def log_operation(
        self,
        db: AsyncSession,
        user_id: str,
        operation: str,
        resource: str = "",
        result: str = "success",
        ip: str = "",
        agent_role: str = "",
    ) -> str:
        """记录操作日志。"""
        record = AuditLog(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            agent_role=agent_role or None,
            operation=operation,
            resource=resource or None,
            result=result,
            ip_address=ip or None,
        )
        db.add(record)
        await db.flush()
        logger.info(f"审计日志: user={user_id}, op={operation}, resource={resource}")
        return str(record.id)


audit_service = AuditService()
