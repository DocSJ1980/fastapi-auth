from typing import Annotated

from fastapi import Form
from pydantic import BaseModel


class Register_User(BaseModel):
    username: Annotated[str, Form()]
    email: Annotated[str, Form()]
    password: Annotated[str, Form()]


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    username: str


class RefreshTokenData(BaseModel):
    email: str
