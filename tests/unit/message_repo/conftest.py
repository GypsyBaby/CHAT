import pytest
import pytest_asyncio

from sqlalchemy import delete

from typing import AsyncGenerator

from src.database.postgresql.connection import SessionWrapper

from src.data.message_repo.postrgesql import MessageRepository
from src.data.message_repo.interface import MessageRepositoryInterface

from src.data.models import Message, User, Group, Chat

from src.core.schemas.chat import ChatType


@pytest_asyncio.fixture
async def message_repo(async_session_wrapper: SessionWrapper) -> AsyncGenerator[None, MessageRepositoryInterface]:
    async with async_session_wrapper.t() as session:
        yield MessageRepository(session)


@pytest_asyncio.fixture
async def insert_test_records(async_session_wrapper: SessionWrapper) -> AsyncGenerator[None, None]:
    async with async_session_wrapper.t() as session:
        session.add(User(id=228, name="Sergey", email="some_email", password="123"))
        await session.flush()

        session.add(Group(id=1337, name="some_group", creator_id=228))
        await session.flush()

        session.add(Chat(id=228, name="some_chat", chat_type=ChatType.PRIVATE.value, group_id=1337))
        await session.flush()

        await session.commit()

    yield

    async with async_session_wrapper.t() as session:
        await session.execute(delete(Message).where(Message.text == "Hello!"))
        await session.execute(delete(Chat).where(Chat.id == 228))
        await session.execute(delete(Group).where(Group.id == 1337))
        await session.execute(delete(User).where(User.id == 228))

        await session.commit()
