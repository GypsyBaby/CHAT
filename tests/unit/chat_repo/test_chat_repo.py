import pytest
from sqlalchemy import select

from src.core.schemas.chat import CreateChatDTO, ChatType
from src.data.chat_repo.interface import ChatRepositoryInterface
from src.data.models import Chat
from src.data.chat_repo.exception import UserNotFound
from src.database.postgresql.connection import SessionWrapper


@pytest.mark.asyncio
@pytest.mark.usefixtures("insert_chat_test_records")
async def test_create_chat_success(
    chat_repo: ChatRepositoryInterface,
    async_session_wrapper: SessionWrapper,
    creator_id: int,
) -> None:
    async with async_session_wrapper.t() as session:
        chat_res = await session.scalars(select(Chat).where(Chat.name == "test_chat"))
        assert not chat_res.fetchall()
    await chat_repo.create_chat(dto=CreateChatDTO(name="test_chat", chat_type=ChatType.PRIVATE, creator_id=creator_id))
    async with async_session_wrapper.t() as session:
        res = await session.scalars(select(Chat).where(Chat.name == "test_chat"))
        model = res.fetchall()[0]
        assert model.name == "test_chat"


@pytest.mark.asyncio
@pytest.mark.usefixtures("insert_chat_test_records")
async def test_create_chat_user_not_found(
    chat_repo: ChatRepositoryInterface,
) -> None:
    with pytest.raises(UserNotFound):
        await chat_repo.create_chat(dto=CreateChatDTO(name="test_chat", chat_type=ChatType.PRIVATE, creator_id=1337))
