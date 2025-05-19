from abc import ABC, abstractmethod
from typing import Optional

from src.core.schemas.message import MessageCreateDTO, MessageDTO, MessageHistory


class MessageRepositoryInterface(ABC):
    @abstractmethod
    async def save_message(self, dto: MessageCreateDTO) -> MessageDTO: ...

    @abstractmethod
    async def mark_message_as_read(self, message_id: int) -> None: ...

    @abstractmethod
    async def get_message_history(
        self, chat_id: int, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> MessageHistory: ...
