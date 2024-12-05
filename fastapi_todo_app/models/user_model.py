from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)  # Simplified
    username: str = Field(index=True, min_length=3, max_length=50)
    email: str = Field(index=True, min_length=5, max_length=50)
    password: str = Field(min_length=8)
    is_verified: bool = Field(default=False)
    verification_tokens: List["VerificationToken"] = Relationship(back_populates="user")
