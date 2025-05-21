import pytest
import pytest_asyncio

from typing import AsyncGenerator

from sqlalchemy import delete

from src.database.postgresql.connection import SessionWrapper

from src.data.chat_repo.interface import ChatRepositoryInterface
from src.data.chat_repo.postgresql import ChatRepository

from src.data.models import Chat, Group, User


@pytest_asyncio.fixture
async def chat_repo(async_session_wrapper: SessionWrapper) -> AsyncGenerator[None, ChatRepositoryInterface]:
    async with async_session_wrapper.t() as session:
        yield ChatRepository(session)



@pytest.fixture
def creator_id() -> int:
    return 1000


@pytest_asyncio.fixture
async def insert_chat_test_records(
    async_session_wrapper: SessionWrapper,
    creator_id: int,
) -> AsyncGenerator[None, None]:
    users = [
        User(id=creator_id, name="Sergey", email="Sergey@mail.ru", password="123"),
    ]
    async with async_session_wrapper.t() as session:
        session.add_all(users)
        await session.commit()

    yield

    async with async_session_wrapper.t() as session:
        await session.execute(delete(Chat).where(Chat.name == "test_chat"))
        await session.commit()
        await session.execute(delete(Group).where(Group.creator_id == creator_id))
        await session.commit()
        for user in users:
            await session.delete(user)

        await session.commit()
