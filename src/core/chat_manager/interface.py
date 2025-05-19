from abc import ABC, abstractmethod
from typing import Protocol

from src.core.schemas.chat import ChatDTO, ChatType


class AsyncConnectionProtocol(Protocol):
    async def send_text(self, data: str) -> None: ...

    async def receive_text(self) -> str: ...


class ChatManagerInterface(ABC):

    @abstractmethod
    async def connect_to_chat(
        self, chat_id: int, user_id: int, connection: AsyncConnectionProtocol
    ) -> None: ...

    @abstractmethod
    async def disconnect_from_chat(self, chat_id: int, user_id: int) -> None: ...

    @abstractmethod
    async def create_chat(
        self, chat_name: str, chat_type: ChatType, creator_id: int
    ) -> ChatDTO: ...

    @abstractmethod
    async def sync_persistent_and_memory_chat_storage(self) -> None: ...
