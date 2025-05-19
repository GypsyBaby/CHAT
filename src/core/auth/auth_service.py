import hashlib

from src.core.auth.jwt import JWTServiceInterface
from src.data.user_repo.interface import UserRepositoryInterface

ACCESS_COOKIE_NAME = "dmitrievs_chat_access_token"


class WrongPasswordError(Exception): ...


class AuthService:

    def __init__(
        self,
        user_repo: UserRepositoryInterface,
        jwt_service: JWTServiceInterface,
        hash_algorithm: str,
    ) -> None:
        self._hash_algorithm = (
            hash_algorithm.lower()
            if hash_algorithm.lower() in hashlib.algorithms_available
            else "sha256"
        )
        self._jwt_service = jwt_service
        self._user_repo = user_repo

    def get_hash(self, string: str) -> str:
        return getattr(hashlib, self._hash_algorithm)(
            string.encode("utf-8")
        ).hexdigest()

    async def authenticate_user_by_credentials(self, login: str, password: str) -> str:
        user = await self._user_repo.get_user_by_login(login)

        if not user.password == self.get_hash(password):
            raise WrongPasswordError

        return self._jwt_service.encode({"user_id": user.id})

    def authenticate_user_by_token(self, token: str) -> dict[str, str]:
        return self._jwt_service.decode(token)
