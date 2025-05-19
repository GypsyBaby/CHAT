import logging

from sqlalchemy import and_, delete, func, select
from sqlalchemy.exc import IntegrityError, NoResultFound

from src.core.schemas.chat import ChatDTO, ChatType, CreateChatDTO
from src.data.base_repo import BasePostgresAsyncRepository
from src.data.chat_repo.exception import (
    ChatNotFound,
    NotCreatorError,
    PrivateChatError,
    UserNotFound,
)
from src.data.chat_repo.interface import ChatRepositoryInterface
from src.data.models import Chat, Group, UserGroup

logger = logging.getLogger(__name__)


class ChatRepository(ChatRepositoryInterface, BasePostgresAsyncRepository[Chat]):

    async def create_chat(self, dto: CreateChatDTO) -> ChatDTO:
        group = Group(name=f"{dto.name}_group", creator_id=dto.creator_id)
        await self.add(group)
        try:
            await self._flush()
        except IntegrityError:
            raise UserNotFound

        chat = Chat(name=dto.name, chat_type=dto.chat_type.value, group_id=group.id)
        await self.add(chat)
        await self._flush()

        await self.commit()

        return ChatDTO(
            id=chat.id,
            name=chat.name,
            chat_type=ChatType(chat.chat_type),
            creator_id=group.creator_id,
            members_ids=[],
        )

    async def get_chat(self, chat_id: int) -> ChatDTO:
        try:
            chat = await self.session.get_one(Chat, chat_id)
        except NoResultFound:
            raise ChatNotFound

        group = await self.session.get_one(Group, chat.group_id)

        user_group_list = await self.session.scalars(
            select(UserGroup).where(UserGroup.group_id == group.id)
        )

        members_ids = [user_group.user_id for user_group in user_group_list]

        return ChatDTO(
            id=chat.id,
            name=chat.name,
            chat_type=ChatType(chat.chat_type),
            creator_id=group.creator_id,
            members_ids=members_ids,
        )

    async def get_all_chats_ids(self) -> list[int]:
        return [chat.id for chat in await self.session.scalars(select(Chat))]

    async def _get_chat_with_group_and_check_owning(
        self, user_id: int, chat_id: int
    ) -> tuple[Chat, Group]:
        try:
            chat = await self.session.get_one(Chat, chat_id)
        except NoResultFound:
            logger.warning(f"Chat wiht id {chat_id} not found")
            raise ChatNotFound

        group = await self.session.get_one(Group, chat.group_id)

        if user_id != group.creator_id:
            logger.warning(
                f"User with id {user_id} is not creator of chat with id {chat_id}"
            )
            raise NotCreatorError

        return chat, group

    async def add_user_to_chat(
        self, user_id: int, new_user_id: int, chat_id: int
    ) -> None:
        chat, group = await self._get_chat_with_group_and_check_owning(user_id, chat_id)

        stmt = (
            select(func.count())
            .select_from(UserGroup)
            .where(UserGroup.group_id == group.id)
        )

        count = await self.session.scalar(stmt)

        if count > 1 and chat.chat_type == ChatType.PRIVATE.value:
            logger.warning(
                f"User with id {user_id} tried to add more than 2 users in private chat"
            )
            raise PrivateChatError

        await self.add(UserGroup(group_id=group.id, user_id=new_user_id))
        try:
            await self._flush()
        except IntegrityError:
            raise UserNotFound

        await self.commit()

    async def remove_user_from_chat(
        self, user_id: int, remove_user_id: int, chat_id: int
    ) -> None:
        _, group = await self._get_chat_with_group_and_check_owning(user_id, chat_id)
        stmt = delete(UserGroup).where(
            and_(UserGroup.group_id == group.id), (UserGroup.user_id == remove_user_id)
        )
        await self.session.execute(stmt)
        await self.session.commit()
