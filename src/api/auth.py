from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm

from settings import settings
from src.api.depends import get_auth_service
from src.core.auth.auth_service import (
    ACCESS_COOKIE_NAME,
    AuthService,
    WrongPasswordError,
)
from src.data.user_repo.exceptions import UserNotFound

auth_router = APIRouter(prefix="/auth")


@auth_router.post("/login")
async def login(
    credentials_data: Annotated[
        OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)
    ],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    response: Response,
) -> Response:
    try:
        token = await auth_service.authenticate_user_by_credentials(
            credentials_data.username, credentials_data.password
        )
    except UserNotFound:
        raise HTTPException(status_code=401, detail=f"login or password is incorrect")
    except WrongPasswordError:
        raise HTTPException(status_code=401, detail=f"login or password is incorrect")

    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=token,
        max_age=settings.JWT_TOKEN_LIFETIME_SEC,
        httponly=True,
        samesite="lax",
    )


@auth_router.post("/logout")
async def logout(response: Response) -> Response:
    response.delete_cookie(key=ACCESS_COOKIE_NAME)
