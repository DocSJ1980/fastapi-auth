from typing import List

from sqlmodel import Field, Relationship, SQLModel

from fastapi_todo_app.models.forgot_password import ForgotPasswordModel
from fastapi_todo_app.models.verification_model import VerificationToken


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=3, max_length=50)
    username: str = Field(index=True, min_length=3, max_length=50)
    email: str = Field(index=True, min_length=5, max_length=50)
    password: str = Field(min_length=8)
    is_verified: bool = Field(default=False)
    role: str = Field(default="user")  # Add role field
    is_two_factor_enabled: bool = Field(default=False)  # Add 2FA field
    is_oauth: bool = Field(default=False)  # Add OAuth field
    verification_tokens: List["VerificationToken"] = Relationship(back_populates="user")
    forgot_password: List["ForgotPasswordModel"] = Relationship(back_populates="user")
