from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)


class Group(Base):

    __tablename__ = "group"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id))


class Chat(Base):

    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    chat_type: Mapped[str] = mapped_column(String, nullable=False)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey(Group.id))


class UserGroup(Base):

    __tablename__ = "user_group"
    __table_args__ = (UniqueConstraint("user_id", "group_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id))
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey(Group.id))


class Message(Base):

    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer, ForeignKey(Chat.id))
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id))
    text: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[int] = mapped_column(Integer, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, nullable=False)
