from typing import Optional

from sqlalchemy import func, select, update

from src.core.schemas.message import MessageCreateDTO, MessageDTO, MessageHistory
from src.data.base_repo import BasePostgresAsyncRepository
from src.data.message_repo.interface import MessageRepositoryInterface
from src.data.models import Message


class MessageRepository(
    MessageRepositoryInterface, BasePostgresAsyncRepository[Message]
):
    async def save_message(self, dto: MessageCreateDTO) -> MessageDTO:
        message_model = Message(**dto.model_dump())
        await self.add(message_model)
        await self.commit()

        return MessageDTO(**message_model.__dict__)

    async def mark_message_as_read(self, message_id: int) -> None:
        stmt = update(Message).values(read=True).where(Message.id == message_id)
        await self.session.execute(stmt)
        await self.commit()

    async def get_message_history(
        self, chat_id: int, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> MessageHistory:
        stmt = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.timestamp)
        )
        stmt_total = select(func.count()).select_from(stmt)
        total = await self.session.scalar(stmt_total)
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        message_records = await self.session.scalars(stmt)
        return MessageHistory(
            items=[MessageDTO(**record.__dict__) for record in message_records],
            total=total,
        )
