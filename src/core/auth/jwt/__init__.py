from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError


class TokenExpiredError(Exception): ...


class InvalidTokenError(Exception): ...


class JWTServiceInterface(ABC):

    @abstractmethod
    def encode(self, payload: dict[str, str]) -> str: ...

    @abstractmethod
    def decode(self, token: str) -> dict[str, str]: ...


class JWTService(JWTServiceInterface):
    def __init__(self, algorithm: str, secret_key: str, token_lifetime: int) -> None:
        self._algorithm = algorithm
        self._secret_key = secret_key
        self._token_lifetime = token_lifetime

    def encode(self, payload: dict[str, str]) -> str:
        payload.update(
            {
                "exp": datetime.now(timezone.utc)
                + timedelta(seconds=self._token_lifetime)
            }
        )
        return jwt.encode(
            payload=payload, key=self._secret_key, algorithm=self._algorithm
        )

    def decode(self, token: str) -> dict[str, str]:
        try:
            return jwt.decode(
                jwt=token, key=self._secret_key, algorithms=(self._algorithm,)
            )
        except ExpiredSignatureError:
            raise TokenExpiredError
        except DecodeError:
            raise InvalidTokenError
