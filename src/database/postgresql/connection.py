from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncContextManager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class ISessionAsyncFactory(ABC):
    @property
    @abstractmethod
    def maker(self) -> async_sessionmaker: ...


class ISessionAsyncWrapper(ABC):

    @property
    @abstractmethod
    def factory(self) -> ISessionAsyncFactory: ...

    @abstractmethod
    def t(self) -> AsyncContextManager[AsyncSession]:
        pass


def create_engine(url: str, echo: bool = False) -> AsyncEngine:
    return create_async_engine(
        url,
        future=True,
        echo=echo,
        pool_pre_ping=False,
        pool_size=20,
        max_overflow=10,
        pool_recycle=1200,
        pool_timeout=6000,
    )


class SessionFactory(ISessionAsyncFactory):
    def __init__(self, engine: AsyncEngine) -> None:
        self._maker = async_sessionmaker(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    @property
    def maker(self) -> async_sessionmaker:
        return self._maker


class SessionWrapper(ISessionAsyncWrapper):
    def __init__(self, factory: ISessionAsyncFactory) -> None:
        self._factory = factory

    @property
    def factory(self) -> ISessionAsyncFactory:
        return self._factory

    def t(self) -> AsyncContextManager[AsyncSession]:
        @asynccontextmanager  # type: ignore
        async def wrapped() -> AsyncContextManager[AsyncSession]:  # type: ignore
            async with self.factory.maker() as session:
                try:
                    yield session  # type: ignore
                except Exception as e:
                    await session.rollback()
                    raise e
                finally:
                    await session.close()

        return wrapped()
