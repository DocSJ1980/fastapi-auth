from typing import Annotated, Optional

from fastapi import Form
from pydantic import BaseModel


class Register_User(BaseModel):
    name: Annotated[str, Form()]
    username: Annotated[str, Form()]
    email: Annotated[str, Form()]
    password: Annotated[str, Form()]


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    username: str
    email: str


class RefreshTokenData(BaseModel):
    email: str
    username: str


class UpdateSettingsRequest(BaseModel):
    is_two_factor_enabled: bool


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class LoginRequest(BaseModel):
    email: str
    password: str
    code: Optional[str] = None


class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    refresh_token: Optional[str] = None


class TwoFactorRequest(BaseModel):
    two_fa_code: str
