from abc import ABC, abstractmethod

from src.core.schemas.chat import ChatDTO, CreateChatDTO


class ChatRepositoryInterface(ABC):

    @abstractmethod
    async def create_chat(self, dto: CreateChatDTO) -> ChatDTO: ...

    @abstractmethod
    async def get_chat(self, chat_id: int) -> ChatDTO: ...

    @abstractmethod
    async def add_user_to_chat(
        self, user_id: int, new_user_id: int, chat_id: int
    ) -> None: ...

    @abstractmethod
    async def remove_user_from_chat(
        self, user_id: int, remove_user_id: int, chat_id: int
    ) -> None: ...

    @abstractmethod
    async def get_all_chats_ids(self) -> list[int]: ...
