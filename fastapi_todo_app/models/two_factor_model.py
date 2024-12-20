from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TwoFactorToken(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    __tablename__ = "two_factor_tokens"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(index=True)
    expires: datetime
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")


class TwoFactorConfirmation(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    __tablename__ = "two_factor_confirmations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    expires: datetime
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")