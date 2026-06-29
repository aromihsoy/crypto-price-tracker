import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from database import Base, get_session




test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
test_session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with test_session_maker() as s:
        yield s
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(session):
    async def override_get_session():
        yield session
    
    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def make_user(client):
    async def _make(username: str, password: str):
        await client.post("/auth/register", json={"username": username, "password": password})
        response = await client.post("/auth/token", data={"username": username, "password": password})
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return _make