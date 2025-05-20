import asyncio
import logging
from datetime import datetime

from fastapi import WebSocket
from fastapi.websockets import WebSocket, WebSocketDisconnect

from src.core.chat_manager.exception import NotMemberError
from src.core.chat_manager.interface import ChatManagerInterface
from src.core.schemas.chat import ChatDTO, ChatType, CreateChatDTO
from src.core.schemas.message import MessageCreateDTO, MessageDTO
from src.core.storage import ConnectionStorage
from src.data.chat_repo.interface import ChatRepositoryInterface
from src.data.message_repo.interface import MessageRepositoryInterface
from src.data.user_repo.interface import UserRepositoryInterface

logger = logging.getLogger(__name__)


class FastapiChatManager(ChatManagerInterface):
    def __init__(
        self,
        connection_storage: ConnectionStorage,
        message_repository: MessageRepositoryInterface,
        chat_repository: ChatRepositoryInterface,
        user_repository: UserRepositoryInterface,
    ) -> None:
        self._connection_storage = connection_storage
        self._message_repository = message_repository
        self._chat_repository = chat_repository
        self._user_repository = user_repository

    async def _wait_until_user_connect_and_send(
        self, message: str, recivier_id: int, chat_id: int, message_id: int
    ) -> None:
        self._connection_storage.add_fresh_message(message_id, chat_id, recivier_id)
        while True:
            recivier_connection = self._connection_storage.get_connection(chat_id, recivier_id)
            if not recivier_connection:
                await asyncio.sleep(3)
                continue

            await recivier_connection.send_text(message)
            self._connection_storage.remover_fresh_message(message_id, chat_id, recivier_id)
            logger.info(f"Message with id {message_id} successfully delivered")
            return

    async def _send_to_all_members(self, chat_id: int, message: MessageDTO) -> None:
        chat = await self._chat_repository.get_chat(chat_id)
        tasks = [
            self._wait_until_user_connect_and_send(message.text, member_id, chat_id, message.id)
            for member_id in chat.members_ids
        ]

        await asyncio.gather(*tasks)

        await self._message_repository.mark_message_as_read(message_id=message.id)

        asyncio.create_task(
            self._wait_until_user_connect_and_send(
                message=f"{message.text}: Message was read by all chat participants.",
                recivier_id=message.sender_id,
                chat_id=chat_id,
                message_id=message.id,
            )
        )

    async def _chat_processing(
        self, chat_id: int, user_id: int, connection: WebSocket
    ) -> None:
        try:
            logger.info(f"User {user_id} connected to chat {chat_id}")
            while True:
                message = await connection.receive_text()
                message = f"User {user_id}: {message}"
                message_dto = await self._message_repository.save_message(
                    dto=MessageCreateDTO(
                        chat_id=chat_id,
                        sender_id=user_id,
                        text=message,
                        timestamp=int(datetime.now().timestamp()),
                    )
                )
                asyncio.create_task(self._send_to_all_members(chat_id, message_dto))

        except WebSocketDisconnect:
            await self.disconnect_from_chat(chat_id, user_id)
            logger.info(f"User {user_id} disconnected from chat {chat_id}")

    async def create_chat(
        self, chat_name: str, chat_type: ChatType, creator_id: int
    ) -> ChatDTO:
        chat_dto = await self._chat_repository.create_chat(
            dto=CreateChatDTO(
                name=chat_name, chat_type=chat_type, creator_id=creator_id
            )
        )
        self._connection_storage.create_chat(chat_dto.id)
        return chat_dto

    async def connect_to_chat(
        self, chat_id: int, user_id: int, connection: WebSocket
    ) -> None:
        chat = await self._chat_repository.get_chat(chat_id)

        if user_id not in chat.members_ids:
            raise NotMemberError

        await connection.accept()

        self._connection_storage.add_user_connection(chat_id, user_id, connection)

        fresh_messages = self._connection_storage.get_fresh_messages(chat_id, user_id)

        msg_hist = await self._message_repository.get_message_history(chat_id=chat_id)

        for msg in msg_hist.items:
            if msg.id not in fresh_messages:
                await connection.send_text(msg.text)

        await self._chat_processing(chat_id, user_id, connection)

    async def disconnect_from_chat(self, chat_id: int, user_id: int) -> None:
        self._connection_storage.remove_user_connection(chat_id, user_id)

    async def sync_persistent_and_memory_chat_storage(self) -> None:
        ids = await self._chat_repository.get_all_chats_ids()
        for chat_id in ids:
            self._connection_storage.create_chat(chat_id)
