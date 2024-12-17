from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime, TypeDecorator
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user_model import User


class TZDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not value.tzinfo:
                value = value.replace(tzinfo=timezone.utc)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if not value.tzinfo:
                value = value.replace(tzinfo=timezone.utc)
        return value


class ForgotPasswordModel(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    __tablename__: str = "forgot_password_tokens"
    id: int | None = Field(default=None, primary_key=True)
    token: str = Field()
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(
        sa_column=Column(TZDateTime(timezone=True)),
        default_factory=lambda: datetime.now(timezone.utc)
    )
    expires_at: datetime = Field(
        sa_column=Column(TZDateTime(timezone=True)),
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=24)
    )
    user: Optional["User"] = Relationship(back_populates="forgot_password")
