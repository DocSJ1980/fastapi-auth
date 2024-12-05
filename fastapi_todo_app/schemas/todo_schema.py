from pydantic import BaseModel
from sqlmodel import Field


class Todo_Create(BaseModel):
    task: str = Field(index=True, min_length=3, max_length=100)


class Todo_Edit(BaseModel):
    task: str = Field(index=True, min_length=3, max_length=100)
    is_completed: bool = Field(default=False)
