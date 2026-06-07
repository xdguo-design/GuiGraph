"""SQLAlchemy 会话管理（异步）。"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import settings

# 创建引擎（SQLite 不支持 pool_size/max_overflow）
_is_sqlite = "sqlite" in settings.DATABASE_URL.lower()

engine_kwargs = {"echo": settings.DEBUG}
if not _is_sqlite:
    engine_kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

# 会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（FastAPI 依赖）。"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """初始化数据库连接池并创建表，并对已有表做轻量迁移。"""
    import app.modules.user.models  # noqa: F401
    import app.modules.organization.models  # noqa: F401
    import app.modules.change.models  # noqa: F401
    import app.modules.upgrade.models  # noqa: F401
    import app.modules.attachment.models  # noqa: F401
    import app.modules.audit.models  # noqa: F401
    import app.modules.knowledge.models  # noqa: F401
    import app.modules.ai.model_manager.models  # noqa: F401
    import app.modules.ai.skill.models  # noqa: F401
    import app.modules.ai.mcp.models  # noqa: F401
    import app.modules.wiki.models  # noqa: F401
    from app.core.database.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # 轻量级迁移：给已存在的表添加新列（SQLite 用 ALTER TABLE ADD COLUMN）
        await _run_lightweight_migrations(conn)


async def _run_lightweight_migrations(conn) -> None:
    """对已有表执行列添加的幂等迁移。"""
    from sqlalchemy import text

    # biz_team 增加 color 列
    await _add_column_if_missing(
        conn,
        table="biz_team",
        column="color",
        ddl="ALTER TABLE biz_team ADD COLUMN color VARCHAR(9)",
    )

    # 兜底：biz_change_item 增加 team_id 列（看板按团队着色用）
    await _add_column_if_missing(
        conn,
        table="biz_change_item",
        column="team_id",
        ddl="ALTER TABLE biz_change_item ADD COLUMN team_id INTEGER",
    )


async def _add_column_if_missing(conn, table: str, column: str, ddl: str) -> None:
    """如果表中缺少列则执行 DDL 添加。SQLite 已有列会抛错，吞掉即可。"""
    from sqlalchemy import text

    res = await conn.execute(text(f"PRAGMA table_info({table})"))
    cols = {row[1] for row in res.fetchall()}
    if column in cols:
        return
    try:
        await conn.execute(text(ddl))
    except Exception as exc:  # noqa: BLE001
        # 表不存在 / 列已存在等情况忽略
        if "duplicate column" in str(exc).lower() or "no such table" in str(exc).lower():
            return
        raise


async def close_db() -> None:
    """关闭数据库连接。"""
    await engine.dispose()
