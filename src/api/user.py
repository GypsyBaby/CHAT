import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.api.depends import get_auth_service, get_user_repo
from src.core.auth.auth_service import AuthService
from src.core.schemas.user import CreateUserDTO, UserDTO
from src.data.user_repo.exceptions import UserAlreadyExists, UserNotFound
from src.data.user_repo.interface import UserRepositoryInterface

logger = logging.getLogger(__name__)

user_router = APIRouter(prefix="/user")


@user_router.post("/")
async def create_user(
    user_dto: CreateUserDTO,
    user_repo: Annotated[UserRepositoryInterface, Depends(get_user_repo)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> JSONResponse:
    user_dto.password = auth_service.get_hash(user_dto.password)
    try:
        user = await user_repo.create_user(dto=user_dto)
    except UserAlreadyExists:
        msg = f"User with name {user_dto.name} already exists"
        logger.warning(msg)
        raise HTTPException(status_code=409, detail=msg)

    return JSONResponse(
        status_code=200,
        content={"message": f"User succefully created with id {user.id}"},
    )


@user_router.get("/{user_id}")
async def get_user(
    user_id: int,
    user_repo: Annotated[UserRepositoryInterface, Depends(get_user_repo)],
) -> UserDTO:
    try:
        user = await user_repo.get_user(user_id)
    except UserNotFound:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    user.password = "***"
    return user
