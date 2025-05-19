import hashlib
import asyncio

from src.settings import settings
from src.database.postgresql.connection import create_engine, SessionFactory, SessionWrapper
from src.data.models import User, Group, UserGroup, Chat

from src.core.schemas.chat import ChatType

from src.core.auth.auth_service import AuthService

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

        await session.commit()


if __name__ == "__main__":
    asyncio.run(load_data())