import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import Template
from pydantic import BaseModel

from src.api.depends import (
    authenticate_user_by_token,
    get_access_token,
    get_auth_service,
    get_chat_manager,
    get_chat_repo,
    get_chat_template,
    get_user_id,
)
from src.core.auth.auth_service import AuthService
from src.core.auth.jwt import InvalidTokenError, TokenExpiredError
from src.core.chat_manager.exception import NotMemberError
from src.core.chat_manager.interface import ChatManagerInterface
from src.core.schemas.chat import ChatDTO, ChatType, CreateChatDTO
from src.data.chat_repo.exception import (
    ChatNotFound,
    NotCreatorError,
    PrivateChatError,
    UserNotFound,
)
from src.data.chat_repo.interface import ChatRepositoryInterface

logger = logging.getLogger(__name__)

chat_router = APIRouter(
    prefix="/chat", dependencies=(Depends(authenticate_user_by_token),)
)


class CreateChatRequestBody(BaseModel):
    name: str
    chat_type: ChatType


@chat_router.post("/")
async def create_chat(
    create_chat_request: CreateChatRequestBody,
    user_id: Annotated[int, Depends(get_user_id)],
    chat_manager: Annotated[ChatManagerInterface, Depends(get_chat_manager)],
) -> JSONResponse:
    try:
        chat_dto = await chat_manager.create_chat(
            create_chat_request.name,
            create_chat_request.chat_type,
            user_id,
        )
    except UserNotFound:
        raise HTTPException(status_code=409, detail=f"User with id {user_id} not found")

    logger.info(f"Chat with id {chat_dto.id} successfully created!")

    return JSONResponse(
        status_code=200,
        content={
            "message": f"Chat succefully created with name {chat_dto.name}",
            "chat_id": chat_dto.id,
        },
    )


@chat_router.post("/{chat_id}")
async def get_chat(
    chat_id: int,
    chat_repo: Annotated[ChatRepositoryInterface, Depends(get_chat_repo)],
) -> ChatDTO:
    try:
        return await chat_repo.get_chat(chat_id=chat_id)
    except ChatNotFound:
        raise HTTPException(status_code=404, detail=f"Chat with id {chat_id} not found")


@chat_router.post("/add_user/{add_user_id}/{chat_id}")
async def add_user_to_chat(
    add_user_id: int,
    chat_id: int,
    user_id: Annotated[int, Depends(get_user_id)],
    chat_repo: Annotated[ChatRepositoryInterface, Depends(get_chat_repo)],
) -> JSONResponse:
    try:
        await chat_repo.add_user_to_chat(
            user_id=user_id, new_user_id=add_user_id, chat_id=chat_id
        )
    except NotCreatorError:
        raise HTTPException(status_code=403, detail="ACCESS FORBIDDEN")
    except ChatNotFound:
        raise HTTPException(status_code=404, detail="CHAT NOT FOUND")
    except UserNotFound:
        raise HTTPException(status_code=404, detail="USER NOT FOUND")
    except PrivateChatError:
        raise HTTPException(status_code=409, detail="TO MANY FOR PRIVATE CHAT")

    msg = f"User with id {add_user_id} added to chat with id {chat_id}"
    logger.info(msg)

    return JSONResponse(
        status_code=200,
        content={
            "message": msg
        },
    )


@chat_router.delete("/add_user/{remove_user_id}/{chat_id}")
async def remove_user_from_chat(
    remove_user_id: int,
    chat_id: int,
    user_id: Annotated[int, Depends(get_user_id)],
    chat_repo: Annotated[ChatRepositoryInterface, Depends(get_chat_repo)],
) -> JSONResponse:
    try:
        await chat_repo.remove_user_from_chat(
            user_id=user_id, remove_user_id=remove_user_id, chat_id=chat_id
        )
    except ChatNotFound:
        raise HTTPException(status_code=404, detail="CHAT NOT FOUND")
    except NotCreatorError:
        raise HTTPException(status_code=403, detail="ACCESS FORBIDDEN")
    
    msg = f"User with id {remove_user_id} removed from chat with id {chat_id}"
    logger.info(msg)

    return JSONResponse(
        status_code=200,
        content={
            "message": msg
        },
    )


@chat_router.get("/{chat_id}")
async def test_endpoint_for_connect_to_ws(
    chat_id: int,
    token: Annotated[str, Depends(get_access_token)],
    chat_template: Annotated[Template, Depends(get_chat_template)],
) -> HTMLResponse:
    html = chat_template.render(chat_id=chat_id, token=token)
    return HTMLResponse(html)


@chat_router.get("/sync/persistent")
async def sync_persistent_and_memory_chat_storage(
    chat_manager: Annotated[ChatManagerInterface, Depends(get_chat_manager)],
) -> JSONResponse:
    await chat_manager.sync_persistent_and_memory_chat_storage()
    return JSONResponse(status_code=200, content={"message": "Success"})


websocket_router = APIRouter(prefix="/connect_to_chat")


@websocket_router.websocket("/{chat_id}/{token}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: int,
    token: str,
    chat_manager: Annotated[ChatManagerInterface, Depends(get_chat_manager)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        payload = auth_service.authenticate_user_by_token(token=token)
    except TokenExpiredError:
        await websocket.close(code=3003, reason="Access token expired")
    except InvalidTokenError:
        await websocket.close(code=3003, reason="Access token invalid")
    if not (user_id := payload.get("user_id")):
        await websocket.close(code=3003, reason="Access token invalid")
    try:
        await chat_manager.connect_to_chat(chat_id, user_id, websocket)
    except NotMemberError:
        logger.warning(f"User {user_id} tried to connect to someone else's chat {chat_id}")
        await websocket.close(code=3003, reason="ACCESS FORBIDDEN")
    except ChatNotFound:
        logger.warning(f"User {user_id} tried to connect to not found chat {chat_id}")
        await websocket.close(code=1000, reason="CHAT NOT FOUND")
