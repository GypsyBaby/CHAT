import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Base(BaseSettings):
    class Config:
        case_sensitive = False

    ENV: str = Field(..., env="DMITRIEV_CHAT_ENV")

    # Application
    DEBUG: bool
    TITLE: str = "DMITRIEV_CHAT APP"
    TEMPLATE_FOLDER: str = "src/api/templates"

    JWT_TOKEN_LIFETIME_SEC: int = 604800
    JWT_SIGNATURE_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str = "h@ck_Me_plea$e"

    PASSWORD_HASH_ALGORITHM: str = "SHA256"

    # Database
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def DATABASE_SYNC_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_ASYNC_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def BASE_DIR(self) -> Path:
        return Path().resolve()


class Local(Base):
    # Application

    DEBUG: bool = True

    ENV: str = "Local"

    # Database
    DB_HOST: str = "dmitrievs_chat_postgres"
    DB_PORT: str = "5432"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "dmitrievs_chat"
    DB_NAME: str = "dmitrievs_chat"

    class Config:
        env_file = "local.env"


class Dev(Base):
    # Application
    DEBUG: bool = True

    # Database
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int = 5432

    class Config:
        env_file = "dev.env"


class Test(Base):
    # Application
    DEBUG: bool = False

    # Database
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int = 5432

    class Config:
        env_file = "test.env"


class Prod(Base):
    # Application
    DEBUG: bool = True

    # Database
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int = 5432

    class Config:
        env_file = "prod.env"


config_map = dict(
    local=Local,
    dev=Dev,
    test=Test,
    prod=Prod,
)


env_variable = os.environ.get("DMITRIEV_CHAT_ENV")
if env_variable is None:
    raise ValueError("Not found 'DMITRIEV_CHAT_ENV' environment variable")
env_variable = env_variable.lower()
if env_variable not in config_map.keys():
    raise ValueError(
        f"Incorrect 'DMITRIEV_CHAT_ENV' environment variable, must be in {list(config_map.keys())}"
    )  # noqa: E501

try:
    settings: Base = config_map[env_variable]()  # type: ignore
except ValueError as e:
    print(f"Error on validate configuration from *.env: {e}")
    raise
