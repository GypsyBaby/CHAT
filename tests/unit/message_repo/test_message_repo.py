import pytest

from sqlalchemy import select

from src.data.message_repo.interface import MessageRepositoryInterface

from src.core.schemas.message import MessageCreateDTO
from src.database.postgresql.connection import SessionWrapper

from src.data.models import Message


@pytest.mark.usefixtures("insert_test_records")
@pytest.mark.asyncio
async def test_save_message_success(message_repo: MessageRepositoryInterface, async_session_wrapper: SessionWrapper) -> None:
    async with async_session_wrapper.t() as session:
        res = await session.scalars(select(Message).where(Message.text == "Hello!"))
        assert not res.fetchall()

    await message_repo.save_message(
        dto=MessageCreateDTO(
            chat_id=228,
            sender_id=228,
            text="Hello!",
            timestamp=123423142,
        )
    )
    async with async_session_wrapper.t() as session:
        res = await session.scalars(select(Message).where(Message.text == "Hello!"))
        assert res.fetchall()