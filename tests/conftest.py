import pytest_asyncio

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine

from src.settings import settings
from src.data.models import Base

from src.database.postgresql.connection import create_engine, SessionFactory, SessionWrapper, AsyncSession


@pytest_asyncio.fixture(scope="function")
async def async_engine() -> AsyncEngine:
    return create_engine(settings.DATABASE_ASYNC_URL)


@pytest_asyncio.fixture(scope="function")
async def async_session_wrapper(async_engine: AsyncEngine) -> SessionWrapper:
    asf = SessionFactory(async_engine)
    asw = SessionWrapper(asf)
    return asw


@pytest_asyncio.fixture(autouse=True, scope="session")
async def init_db() -> AsyncGenerator[None, None]:
    engine = create_engine(settings.DATABASE_ASYNC_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
