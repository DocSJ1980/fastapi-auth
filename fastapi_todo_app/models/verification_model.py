from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user_model import User

class VerificationToken(SQLModel, table=True):
    __tablename__ = "verification_tokens"
    
    token: str = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))
    is_used: bool = Field(default=False)
    
    user: Optional["User"] = Relationship(back_populates="verification_tokens")
