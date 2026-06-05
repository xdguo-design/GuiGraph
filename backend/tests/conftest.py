"""测试配置。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.config.settings import settings

# 测试用 SQLite（内存数据库）
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def client():
    """测试客户端。"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session():
    """测试数据库会话。"""
    async def _get_session():
        async with TestingSessionLocal() as session:
            yield session
            await session.close()
    return _get_session


@pytest.fixture
def auth_token():
    """测试用有效 Token。"""
    from app.core.security.jwt import create_access_token
    return create_access_token({"sub": "user_001", "username": "test_user", "role": "editor"})


@pytest.fixture
def admin_token():
    """测试用管理员 Token。"""
    from app.core.security.jwt import create_access_token
    return create_access_token({"sub": "admin_001", "username": "admin", "role": "system_admin"})
