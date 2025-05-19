from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.api.depends import get_chat_repo, get_message_repo, get_user_id
from src.core.schemas.message import MessageHistory
from src.data.chat_repo.exception import ChatNotFound
from src.data.chat_repo.interface import ChatRepositoryInterface
from src.data.message_repo.interface import MessageRepositoryInterface

history_router = APIRouter(prefix="/history")


class HistoryPaginationParams(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None


@history_router.get("/{chat_id}")
async def get_chat_history(
    chat_id: int,
    user_id: Annotated[int, Depends(get_user_id)],
    pagination: Annotated[HistoryPaginationParams, Query()],
    message_repo: Annotated[MessageRepositoryInterface, Depends(get_message_repo)],
    chat_repo: Annotated[ChatRepositoryInterface, Depends(get_chat_repo)],
) -> MessageHistory:
    try:
        chat = await chat_repo.get_chat(chat_id)
    except ChatNotFound:
        raise HTTPException(status_code=404, detail="CHAT NOT FOUND")

    if user_id not in chat.members_ids:
        raise HTTPException(status_code=403, detail="YOU ARE NOT A MEMBER OF THAT CHAT")

    return await message_repo.get_message_history(
        chat_id, limit=pagination.limit, offset=pagination.offset
    )
