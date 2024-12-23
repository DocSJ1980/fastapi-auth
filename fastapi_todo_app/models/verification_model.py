from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from fastapi_todo_app.settings import EMAIL_VERIFICATION_TOKEN_EXPIRY_TIME

if TYPE_CHECKING:
    from .user_model import User


class VerificationToken(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    __tablename__: str = "email_verification_tokens"
    id: int | None = Field(default=None, primary_key=True)
    token: str = Field()
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now()
        + timedelta(minutes=EMAIL_VERIFICATION_TOKEN_EXPIRY_TIME)
    )
    # user: Optional["User"] = Relationship(back_populates="verification_tokens")

    user: Optional["User"] = Relationship()
