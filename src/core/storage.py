from typing import Optional, Union, Set
from src.core.chat_manager.interface import AsyncConnectionProtocol


class ConnectionStorage:
    def __init__(self) -> None:
        self._chats: dict[
            int, dict[int, dict[str, Union[AsyncConnectionProtocol, Set]]]
        ] = (
            {}
        )  # {chat_id: {"connections": {user_id: WebSocketObject}}, "fresh_message_ids": {user_id: set()}}

    def create_chat(self, chat_id: int) -> None:
        self._chats[chat_id] = {"connections": {}, "fresh_message_ids": {}}

    def get_chat(self, chat_id: int) -> dict[int, dict[str, Union[AsyncConnectionProtocol, Set]]]:
        return self._chats[chat_id]

    def add_user_connection(
        self, chat_id: int, user_id: int, connection: AsyncConnectionProtocol
    ) -> None:
        self._chats[chat_id]["connections"].update({user_id: connection})
        if user_id not in self._chats[chat_id]["fresh_message_ids"]:
            self._chats[chat_id]["fresh_message_ids"].update({user_id: set()})

    def remove_user_connection(self, chat_id: int, user_id: int) -> None:
        del self._chats[chat_id]["connections"][user_id]

    def add_fresh_message(self, message_id: int, chat_id: int, user_id: int) -> None:
        if user_id in self._chats[chat_id]["fresh_message_ids"]:
            self._chats[chat_id]["fresh_message_ids"][user_id].add(message_id)
        else:
            self._chats[chat_id]["fresh_message_ids"].update({user_id: {message_id}})

    def remover_fresh_message(self, message_id: int, chat_id: int, user_id: int) -> None:
        self._chats[chat_id]["fresh_message_ids"][user_id].discard(message_id)
    
    def get_fresh_messages(self, chat_id: int, user_id: int) -> Set:
        return self._chats.get(chat_id)["fresh_message_ids"].get(user_id)

    def get_connection(self, chat_id: int, user_id: int) -> Optional[AsyncConnectionProtocol]:
        return self._chats.get(chat_id)["connections"].get(user_id)

connection_storage = ConnectionStorage()
