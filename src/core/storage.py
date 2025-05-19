from src.core.chat_manager.interface import AsyncConnectionProtocol


class ConnectionStorage:
    def __init__(self) -> None:
        self._chats: dict[int, dict[int, AsyncConnectionProtocol]] = (
            {}
        )  # {chat_id: {user_id: WebSocketObject}}

    def create_chat(self, chat_id: int) -> None:
        self._chats[chat_id] = {}

    def get_chat(self, chat_id: int) -> dict[int, AsyncConnectionProtocol]:
        return self._chats[chat_id]

    def add_user_connection(
        self, chat_id: int, user_id: int, connection: AsyncConnectionProtocol
    ) -> None:
        self._chats[chat_id].update({user_id: connection})

    def remove_user_connection(self, chat_id: int, user_id: int) -> None:
        del self._chats[chat_id][user_id]


connection_storage = ConnectionStorage()
