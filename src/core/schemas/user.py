from pydantic import BaseModel, SecretStr


class CreateUserDTO(BaseModel):
    name: str
    email: str
    password: str


class UserDTO(BaseModel):
    id: int
    name: str
    email: str
    password: str
