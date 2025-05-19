import pytest
import pytest_asyncio

from sqlalchemy import delete

from typing import AsyncGenerator

from src.database.postgresql.connection import SessionWrapper

from src.data.user_repo.postgresql import UserRepository
from src.data.user_repo.interface import UserRepositoryInterface

from src.data.models import User


@pytest_asyncio.fixture
async def user_repo(
    async_session_wrapper: SessionWrapper,
) -> AsyncGenerator[None, UserRepositoryInterface]:
    async with async_session_wrapper.t() as session:
        yield UserRepository(session)


@pytest_asyncio.fixture
async def insert_test_records(
    async_session_wrapper: SessionWrapper,
) -> AsyncGenerator[None, None]:
    users = [
        User(id=1000, name="Sergey", email="Sergey@mail.ru", password="123"),
        User(id=1001, name="Arina", email="Arina@mail.ru", password="123"),
        User(id=1002, name="Vlad", email="Vlad@mail.ru", password="123"),
    ]
    async with async_session_wrapper.t() as session:
        session.add_all(users)
        await session.commit()

    yield

    async with async_session_wrapper.t() as session:
        for user in users:
            await session.delete(user)

        await session.commit()


@pytest_asyncio.fixture
async def cleand_db_after_create_test(
    async_session_wrapper: SessionWrapper,
) -> AsyncGenerator[None, None]:
    yield
    async with async_session_wrapper.t() as session:
        await session.execute(delete(User).where(User.name == "Amogus"))
        await session.commit()
