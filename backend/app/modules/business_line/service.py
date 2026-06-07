"""业务线服务层。"""

from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.business_line.models import BusinessLine


class BusinessLineService:
    """业务线业务逻辑。"""

    async def list_lines(
        self,
        db: AsyncSession,
        status: str = "",
    ) -> list[dict]:
        """查询业务线列表。"""
        q = select(BusinessLine).order_by(BusinessLine.sort_order, BusinessLine.id)
        if status:
            q = q.where(BusinessLine.status == status)
        rows = (await db.execute(q)).scalars().all()
        return [r.to_dict() for r in rows]

    async def get_line(self, db: AsyncSession, line_id: int) -> dict | None:
        """获取业务线详情。"""
        row = await db.get(BusinessLine, line_id)
        return row.to_dict() if row else None

    async def create_line(self, db: AsyncSession, data: dict) -> dict:
        """创建业务线。"""
        record = BusinessLine(**data)
        db.add(record)
        await db.flush()
        logger.info(f"创建业务线: {data.get('name')}")
        return record.to_dict()

    async def update_line(self, db: AsyncSession, line_id: int, data: dict) -> dict | None:
        """更新业务线。"""
        record = await db.get(BusinessLine, line_id)
        if not record:
            return None
        for k, v in data.items():
            if hasattr(record, k) and k != "id":
                setattr(record, k, v)
        await db.flush()
        logger.info(f"更新业务线: {line_id}")
        return record.to_dict()

    async def delete_line(self, db: AsyncSession, line_id: int) -> bool:
        """删除业务线。"""
        record = await db.get(BusinessLine, line_id)
        if not record:
            return False
        await db.delete(record)
        logger.info(f"删除业务线: {line_id}")
        return True


business_line_service = BusinessLineService()
