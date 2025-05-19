from enum import Enum

from pydantic import BaseModel


class ChatType(Enum):
    PRIVATE = "PRIVATE"
    GROUP = "GROUP"


class ChatDTO(BaseModel):
    id: int
    name: str
    chat_type: ChatType
    creator_id: int
    members_ids: list[int]


class CreateChatDTO(BaseModel):
    name: str
    chat_type: ChatType
    creator_id: int
