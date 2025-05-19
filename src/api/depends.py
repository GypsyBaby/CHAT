from typing import Annotated, AsyncGenerator, Generator

from fastapi import Depends, HTTPException, Request
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.auth.auth_service import ACCESS_COOKIE_NAME, AuthService
from src.core.auth.jwt import (
    InvalidTokenError,
    JWTService,
    JWTServiceInterface,
    TokenExpiredError,
)
from src.core.chat_manager.fastapi import FastapiChatManager
from src.core.chat_manager.interface import ChatManagerInterface
from src.core.storage import connection_storage
from src.data.chat_repo.interface import ChatRepositoryInterface
from src.data.chat_repo.postgresql import ChatRepository
from src.data.message_repo.interface import MessageRepositoryInterface
from src.data.message_repo.postrgesql import MessageRepository
from src.data.user_repo.interface import UserRepositoryInterface
from src.data.user_repo.postgresql import UserRepository
from src.database.postgresql.connection import (
    SessionFactory,
    SessionWrapper,
    create_engine,
)
from src.settings import settings


def get_async_engine() -> AsyncEngine:
    return create_engine(url=settings.DATABASE_ASYNC_URL)


def get_async_session_factory(
    async_engine: Annotated[AsyncEngine, Depends(get_async_engine)],
) -> SessionFactory:
    return SessionFactory(engine=async_engine)


def get_async_session_wrapper(
    async_session_factory: Annotated[
        SessionFactory, Depends(get_async_session_factory)
    ],
) -> SessionWrapper:
    return SessionWrapper(factory=async_session_factory)


async def get_user_repo(
    async_session_wrapper: Annotated[
        SessionWrapper, Depends(get_async_session_wrapper)
    ],
) -> AsyncGenerator[None, UserRepositoryInterface]:
    async with async_session_wrapper.t() as session:
        yield UserRepository(session=session)


async def get_chat_repo(
    async_session_wrapper: Annotated[
        SessionWrapper, Depends(get_async_session_wrapper)
    ],
) -> AsyncGenerator[None, ChatRepositoryInterface]:
    async with async_session_wrapper.t() as session:
        yield ChatRepository(session=session)


async def get_message_repo(
    async_session_wrapper: Annotated[
        SessionWrapper, Depends(get_async_session_wrapper)
    ],
) -> AsyncGenerator[None, MessageRepositoryInterface]:
    async with async_session_wrapper.t() as session:
        yield MessageRepository(session=session)


def get_jinja_environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(settings.TEMPLATE_FOLDER), autoescape=select_autoescape
    )


def get_chat_template(
    env: Annotated[Environment, Depends(get_jinja_environment)],
) -> Template:
    return env.get_template("chat.html")


def get_chat_manager(
    chat_repo: Annotated[ChatRepositoryInterface, Depends(get_chat_repo)],
    user_repo: Annotated[UserRepositoryInterface, Depends(get_user_repo)],
    message_repo: Annotated[MessageRepositoryInterface, Depends(get_message_repo)],
) -> Generator[None, None, ChatManagerInterface]:
    yield FastapiChatManager(
        connection_storage=connection_storage,
        message_repository=message_repo,
        chat_repository=chat_repo,
        user_repository=user_repo,
    )


def get_jwt_service() -> JWTServiceInterface:
    return JWTService(
        algorithm=settings.JWT_SIGNATURE_ALGORITHM,
        secret_key=settings.JWT_SECRET_KEY,
        token_lifetime=settings.JWT_TOKEN_LIFETIME_SEC,
    )


def get_auth_service(
    jwt_service: Annotated[JWTServiceInterface, Depends(get_jwt_service)],
    user_repo: Annotated[UserRepositoryInterface, Depends(get_user_repo)],
) -> AuthService:
    return AuthService(
        user_repo=user_repo,
        jwt_service=jwt_service,
        hash_algorithm=settings.PASSWORD_HASH_ALGORITHM,
    )


def get_access_token(request: Request) -> str:
    token = request.cookies.get(ACCESS_COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=403,
            detail="Authentication token is missing.",
        )
    return token


def authenticate_user_by_token(
    token: Annotated[str, Depends(get_access_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, str]:
    try:
        payload = auth_service.authenticate_user_by_token(token)
    except TokenExpiredError:
        raise HTTPException(status_code=403, detail="Access token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=403, detail="Access token invalid")

    return payload


def get_user_id(
    token_payload: Annotated[dict[str, str], Depends(authenticate_user_by_token)],
) -> str:
    if not (user_id := token_payload.get("user_id")):
        raise HTTPException(status_code=403, detail="Access token invalid")
    return user_id
