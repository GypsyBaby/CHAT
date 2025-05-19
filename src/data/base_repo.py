from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.postgresql.connection import (
    ISessionAsyncFactory,
    ISessionAsyncWrapper,
)

_EntityT = TypeVar("_EntityT")


class BasePostgresAsyncRepository(Generic[_EntityT]):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise NotImplementedError("Session was not setup")
        return self._session

    async def add(self, entity: _EntityT) -> None:
        self.session.add(entity)

    async def commit(self):
        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise

    async def _flush(self):
        try:
            await self.session.flush()
        except Exception as e:
            await self.session.rollback()
            raise
