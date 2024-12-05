# Step-1: Create Database on Neon
# Step-2: Create .env file for environment variables
# Step-3: Create setting.py file for encrypting DatabaseURL
# Step-4: Create a Model
# Step-5: Create Engine
# Step-6: Create function for table creation
# Step-7: Create function for session management
# Step-8: Create contex manager for app lifespan
# Step-9: Create all endpoints of todo app

from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Annotated, AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, col, select

from fastapi_todo_app.services.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    credentials_exception,
    get_current_user,
    validate_refresh_token,
)
from fastapi_todo_app.db import create_tables, get_session
from fastapi_todo_app.models.todo_model import Todo
from fastapi_todo_app.models.user_model import User
from fastapi_todo_app.models.verification_model import VerificationToken
from fastapi_todo_app.router import user_router
from fastapi_todo_app.schemas.todo_schema import Todo_Create, Todo_Edit
from fastapi_todo_app.schemas.user_schema import Token
from fastapi_todo_app.settings import EXPIRY_TIME, REFRESH_TOKEN_EXPIRY_TIME


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Initializing database...")
    create_tables()
    print("Database initialized")
    yield


app: FastAPI = FastAPI(
    lifespan=lifespan,
    title="FastAPI Todo App",
    description="A simple todo app built with FastAPI",
    version="0.1.0",
)

app.include_router(router=user_router.user_router)


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    expiry_time = timedelta(minutes=float(str(EXPIRY_TIME)))
    access_token = create_access_token({"sub": form_data.username}, expiry_time)
    expiry_time = timedelta(days=int(str(REFRESH_TOKEN_EXPIRY_TIME)))
    refresh_token = create_refresh_token({"sub": user.email}, expiry_time)
    return Token(
        access_token=access_token, token_type="bearer", refresh_token=refresh_token
    )


@app.post("/token/refresh", response_model=Token)
async def refresh_token(
    old_refresh_token: str,
    session: Annotated[Session, Depends(get_session)],
):
    user = validate_refresh_token(old_refresh_token, session)
    if not user:
        raise credentials_exception
    expiry_time = timedelta(minutes=float(str(EXPIRY_TIME)))
    access_token = create_access_token({"sub": user.username}, expiry_time)
    expiry_time = timedelta(days=int(str(REFRESH_TOKEN_EXPIRY_TIME)))
    refresh_token = create_refresh_token({"sub": user.email}, expiry_time)
    return Token(
        access_token=access_token, token_type="bearer", refresh_token=refresh_token
    )


@app.post("/todos/", response_model=Todo)
async def create_todo(
    current_user: Annotated[User, Depends(get_current_user)],
    todo: Todo_Create,
    session: Annotated[Session, Depends(get_session)],
    response: Response,
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.id is None:
        raise HTTPException(status_code=500, detail="User ID is not set")
    new_todo = Todo(
        task=todo.task,
        user_id=current_user.id,  # Set the user_id from the authenticated user
    )
    session.add(new_todo)
    session.commit()
    session.refresh(new_todo)
    response.status_code = 201
    return new_todo


@app.get("/todos/", response_model=list[Todo])
async def get_all_todos(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    statement = (
        select(Todo).where(Todo.user_id == current_user.id).order_by(col(Todo.id))
    )
    todos = session.exec(statement).all()
    if todos:
        return todos
    else:
        raise HTTPException(status_code=404, detail="No todos found")


@app.get("/todos/{id}", response_model=Todo)
async def get_single_todo(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    statement = (
        select(Todo)
        .where(Todo.user_id == current_user.id)
        .where(Todo.id == id)
        .order_by(col(Todo.id))
    )
    todo = session.exec(statement).first()
    if todo:
        return todo
    else:
        raise HTTPException(status_code=404, detail="No todo found")


@app.put("/todos/{id}", response_model=Todo)
async def update_todo(
    id: int,
    todo: Todo_Edit,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    statement = select(Todo).where(Todo.user_id == current_user.id).where(Todo.id == id)

    existing_todo = session.exec(statement).first()
    if existing_todo:
        existing_todo.task = todo.task
        existing_todo.is_completed = todo.is_completed
        session.add(existing_todo)
        session.commit()
        session.refresh(existing_todo)
        return existing_todo
    else:
        raise HTTPException(status_code=404, detail="Todo not found")


@app.delete("/todos/{id}")
async def delete_todo(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    response: Response,
):
    statement = select(Todo).where(Todo.user_id == current_user.id).where(Todo.id == id)
    existing_todo = session.exec(statement).first()
    if existing_todo:
        session.delete(existing_todo)
        session.commit()
        response.status_code = 202
        return {"message": "Task successfully deleted"}
    else:
        raise HTTPException(status_code=404, detail="Todo not found")
