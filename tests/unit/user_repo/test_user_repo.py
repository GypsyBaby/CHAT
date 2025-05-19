import pytest

from sqlalchemy import select

from src.core.schemas.user import UserDTO

from src.data.user_repo.interface import UserRepositoryInterface
from src.data.user_repo.exceptions import UserNotFound, UserAlreadyExists

from src.database.postgresql.connection import SessionWrapper

from src.data.models import User
from src.core.schemas.user import CreateUserDTO


@pytest.mark.usefixtures("insert_test_records")
@pytest.mark.asyncio
async def test_get_user_success(user_repo: UserRepositoryInterface) -> None:
    user = await user_repo.get_user(user_id=1000)
    assert isinstance(user, UserDTO)
    assert user.id == 1000
    assert user.name == "Sergey"


@pytest.mark.usefixtures("insert_test_records")
@pytest.mark.asyncio
async def test_get_user_not_found(user_repo: UserRepositoryInterface) -> None:
    with pytest.raises(UserNotFound):
        await user_repo.get_user(user_id=228)


@pytest.mark.usefixtures("cleand_db_after_create_test")
@pytest.mark.asyncio
async def test_create_user_succeses(user_repo: UserRepositoryInterface, async_session_wrapper: SessionWrapper) -> None:
    async with async_session_wrapper.t() as session:
        res = await session.scalars(select(User).where(User.name == "Amogus"))
        assert not res.fetchall()
    
    await user_repo.create_user(dto=CreateUserDTO(name="Amogus", email="some_email", password="123"))

    async with async_session_wrapper.t() as session:
        res = await session.scalars(select(User).where(User.name == "Amogus"))
        assert res.fetchall()


@pytest.mark.usefixtures("insert_test_records")
@pytest.mark.asyncio
async def test_create_user_already_exists(user_repo: UserRepositoryInterface, async_session_wrapper: SessionWrapper) -> None:
    with pytest.raises(UserAlreadyExists):
        await user_repo.create_user(dto=CreateUserDTO(name="Sergey", email="some_email", password="123"))

