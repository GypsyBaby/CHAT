import logging

logger = logging.getLogger(__name__)


async def sync_persistent_and_memory_chat_storage() -> None:
    from src.core.chat_manager.fastapi import FastapiChatManager
    from src.core.storage import connection_storage
    from src.data.chat_repo.postgresql import ChatRepository
    from src.data.message_repo.postrgesql import MessageRepository
    from src.data.user_repo.postgresql import UserRepository
    from src.database.postgresql.connection import create_engine, SessionFactory, SessionWrapper
    from src.settings import settings
    ssw = SessionWrapper(SessionFactory(create_engine(settings.DATABASE_ASYNC_URL)))
    async with ssw.t() as session:
        chat_manager = FastapiChatManager(
            connection_storage=connection_storage,
            message_repository=MessageRepository(session),
            chat_repository=ChatRepository(session),
            user_repository=UserRepository(session),
        )
        await chat_manager.sync_persistent_and_memory_chat_storage()
        logger.info("Persistent and operative storages synced!")
