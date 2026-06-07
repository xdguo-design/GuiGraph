"""产品线服务层。"""

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product_line.models import ProductLine


class ProductLineService:
    """产品线业务逻辑。"""

    async def list_lines(
        self,
        db: AsyncSession,
        business_line_id: int | None = None,
        status: str = "",
    ) -> list[dict]:
        """查询产品线列表。"""
        q = select(ProductLine).order_by(ProductLine.sort_order, ProductLine.id)
        if business_line_id:
            q = q.where(ProductLine.business_line_id == business_line_id)
        if status:
            q = q.where(ProductLine.status == status)
        rows = (await db.execute(q)).scalars().all()
        return [r.to_dict() for r in rows]

    async def get_line(self, db: AsyncSession, line_id: int) -> dict | None:
        """获取产品线详情。"""
        row = await db.get(ProductLine, line_id)
        return row.to_dict() if row else None

    async def create_line(self, db: AsyncSession, data: dict) -> dict:
        """创建产品线。"""
        record = ProductLine(**data)
        db.add(record)
        await db.flush()
        logger.info(f"创建产品线: {data.get('name')}")
        return record.to_dict()

    async def update_line(self, db: AsyncSession, line_id: int, data: dict) -> dict | None:
        """更新产品线。"""
        record = await db.get(ProductLine, line_id)
        if not record:
            return None
        for k, v in data.items():
            if hasattr(record, k) and k != "id":
                setattr(record, k, v)
        await db.flush()
        logger.info(f"更新产品线: {line_id}")
        return record.to_dict()

    async def delete_line(self, db: AsyncSession, line_id: int) -> bool:
        """删除产品线。"""
        record = await db.get(ProductLine, line_id)
        if not record:
            return False
        await db.delete(record)
        logger.info(f"删除产品线: {line_id}")
        return True


product_line_service = ProductLineService()
