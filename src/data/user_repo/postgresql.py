from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound

from src.core.schemas.user import CreateUserDTO, UserDTO
from src.data.base_repo import BasePostgresAsyncRepository
from src.data.models import User
from src.data.user_repo.exceptions import UserAlreadyExists, UserNotFound
from src.data.user_repo.interface import UserRepositoryInterface


class UserRepository(UserRepositoryInterface, BasePostgresAsyncRepository[User]):

    async def create_user(self, dto: CreateUserDTO) -> UserDTO:
        model = User(**dto.model_dump())
        await self.add(model)
        try:
            await self.commit()
        except IntegrityError:
            raise UserAlreadyExists
        return UserDTO(**model.__dict__)

    async def get_user(self, user_id: int) -> UserDTO:
        try:
            user = await self.session.get_one(User, user_id)
        except NoResultFound:
            raise UserNotFound
        return UserDTO(**user.__dict__)

    async def get_user_by_login(self, login: str) -> UserDTO:
        stmt = select(User).where(User.name == login)
        if not (model := await self.session.scalar(stmt)):
            raise UserNotFound
        return UserDTO(**model.__dict__)
