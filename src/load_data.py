import hashlib
import asyncio

from src.settings import settings
from src.database.postgresql.connection import create_engine, SessionFactory, SessionWrapper
from src.data.models import User, Group, UserGroup, Chat, Message

from src.core.schemas.chat import ChatType

hashed_pw = getattr(hashlib, settings.PASSWORD_HASH_ALGORITHM.lower())("12345".encode("utf-8")).hexdigest()

USERS = [
    User(id=1000, name="Sergey", email="Sergey@mail.ru", password=hashed_pw),
    User(id=1001, name="Arina", email="Arina@mail.ru", password=hashed_pw),
    User(id=1002, name="Vlad", email="Vlad@mail.ru", password=hashed_pw),
]

GROUPS = [
    Group(id=1000, name="Personal_Chat_Group", creator_id=1000),
    Group(id=1001, name="Group_Chat_Group", creator_id=1000),
    ]


USERGROUPS = [
    UserGroup(user_id=1000, group_id=1000), UserGroup(user_id=1001, group_id=1000),
    UserGroup(user_id=1000, group_id=1001), UserGroup(user_id=1001, group_id=1001), UserGroup(user_id=1002, group_id=1001),
]


CHATS = [
    Chat(id=1000, name="Private_chat", chat_type=ChatType.PRIVATE.value, group_id=1000),
    Chat(id=1001, name="Group_chat", chat_type=ChatType.GROUP.value, group_id=1001),
]

MESSAGES = [
    Message(id=1000, chat_id=1000, sender_id=1000, text="Hello! I am Sergey!", timestamp=1747765539, read=True),
    Message(id=1001, chat_id=1000, sender_id=1001, text="Hello! I am Arina!", timestamp=1747765540, read=True),
    Message(id=1002, chat_id=1001, sender_id=1000, text="Hello everybody! I am Sergey!", timestamp=1747765541, read=True),
    Message(id=1003, chat_id=1001, sender_id=1001, text="Hello everybody! I am Arina!", timestamp=1747765542, read=True),
    Message(id=1004, chat_id=1001, sender_id=1002, text="Hello everybody! I am Vlad!", timestamp=1747765542, read=True),
]


async def load_data() -> None:
    asw = SessionWrapper(SessionFactory(create_engine(settings.DATABASE_ASYNC_URL)))

    async with asw.t() as session:
        session.add_all(USERS)
        await session.flush()

        session.add_all(GROUPS)
        await session.flush()

        session.add_all(USERGROUPS)
        await session.flush()

        session.add_all(CHATS)
        await session.flush()

        session.add_all(MESSAGES)
        await session.flush()

        await session.commit()


if __name__ == "__main__":
    asyncio.run(load_data())