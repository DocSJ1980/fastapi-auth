from sqlmodel import Field, SQLModel


class Todo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)  # Simplified
    task: str = Field(index=True, min_length=3, max_length=100)
    is_completed: bool = Field(default=False)
    user_id: int = Field(foreign_key="user.id")  # Simplified
