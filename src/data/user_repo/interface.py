from abc import ABC, abstractmethod

from src.core.schemas.user import CreateUserDTO, UserDTO


class UserRepositoryInterface(ABC):

    @abstractmethod
    async def create_user(self, dto: CreateUserDTO) -> UserDTO: ...

    @abstractmethod
    async def get_user(self, user_id: int) -> UserDTO: ...

    @abstractmethod
    async def get_user_by_login(self, login: str) -> UserDTO: ...
