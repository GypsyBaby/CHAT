from pydantic import BaseModel


class MessageCreateDTO(BaseModel):
    chat_id: int
    sender_id: int
    text: str
    timestamp: int
    read: bool = False


class MessageDTO(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    text: str
    timestamp: int
    read: bool = False


class MessageHistory(BaseModel):
    items: list[MessageDTO]
    total: int
