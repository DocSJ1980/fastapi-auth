
from sqlmodel import Field, SQLModel

# from fastapi_todo_app.models.forgot_password import ForgotPasswordModel
# from fastapi_todo_app.models.two_factor_model import (
#     TwoFactorConfirmation,
#     TwoFactorToken,
# )
# from fastapi_todo_app.models.verification_model import VerificationToken


class User(SQLModel, table=True):
    __tablename__ = "user"
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=3, max_length=50)
    username: str = Field(index=True, min_length=3, max_length=50)
    email: str = Field(index=True, min_length=5, max_length=50)
    password: str = Field(min_length=8)
    is_verified: bool = Field(default=False)
    role: str = Field(default="user")
    is_two_factor_enabled: bool = Field(default=False)

    # Relationships
    # two_factor_tokens: List["TwoFactorToken"] = Relationship(back_populates="user")
    # two_factor_confirmations: List["TwoFactorConfirmation"] = Relationship(
    #     back_populates="user"
    # )
    # verification_tokens: List[VerificationToken] = Relationship(back_populates="user")
    # forgot_password_tokens: List[ForgotPasswordModel] = Relationship(
    #     back_populates="user"
    # )
