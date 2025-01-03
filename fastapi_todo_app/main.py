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
from datetime import datetime, timedelta, timezone
from typing import Annotated, AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

# from sqlalchemy import and_
from sqlmodel import Session, col, select

from fastapi_todo_app.db import create_tables, get_session
from fastapi_todo_app.models.todo_model import Todo
from fastapi_todo_app.models.two_factor_model import (
    TwoFactorConfirmation,
    TwoFactorToken,
)
from fastapi_todo_app.models.user_model import User
from fastapi_todo_app.router import user_router
from fastapi_todo_app.schemas.todo_schema import Todo_Create, Todo_Edit
from fastapi_todo_app.schemas.user_schema import (
    LoginRequest,
    LoginResponse,
    Token,
    TwoFactorRequest,
)
from fastapi_todo_app.services.auth import (
    authenticate_user,
    create_access_token,
    create_credentials_exception,
    create_refresh_token,
    generate_two_factor_token,
    get_current_user,
    validate_refresh_token,
)
from fastapi_todo_app.services.email_service import send_two_factor_email
from fastapi_todo_app.settings import (
    EXPIRY_TIME,
    FRONTEND_URL,
    REFRESH_TOKEN_EXPIRY_TIME,
)

origins = [
    FRONTEND_URL,
    "http://localhost:3000",
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_tables()
    yield


app: FastAPI = FastAPI(
    lifespan=lifespan,
    title="FastAPI Todo App",
    description="A simple todo app built with FastAPI",
    version="0.1.0",
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router=user_router.user_router)
print(f"Frontend URL: {FRONTEND_URL}")


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/two-fa-confirm", response_model=LoginResponse)
async def check_two_factor_confirmation(
    request: TwoFactorRequest,
    session: Session = Depends(get_session),
):
    token = request.two_fa_code  # Get the code from the request body
    statement = select(TwoFactorToken).where(TwoFactorToken.token == token)
    token_record = session.exec(statement).first()

    if not token_record:
        raise HTTPException(status_code=404, detail="Invalid 2FA code")

    token_expires = token_record.expires.replace(tzinfo=timezone.utc)
    if token_expires < datetime.now(timezone.utc):
        session.delete(token_record)
        session.commit()
        raise HTTPException(status_code=400, detail="2FA code has expired")

    statement = select(User).where(User.id == token_record.user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    two_factor_confirmation = TwoFactorConfirmation(
        expires=datetime.now() + timedelta(minutes=10), user_id=user.id
    )
    session.delete(token_record)
    session.add(two_factor_confirmation)
    session.commit()

    return LoginResponse(
        success=True,
        message="2FA verified successfully",
        access_token=None,
        token_type=None,
        refresh_token=None,
    )


@app.post("/token", response_model=LoginResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    print("🚀 ~ file: main.py:134 ~ form_data:", form_data.username, form_data.password)
    try:
        user = authenticate_user(form_data.username, form_data.password, session)
    except Exception as e:
        print(f"Error authenticating user: {str(e)}")
        raise create_credentials_exception(str(e))

    if not user:
        raise create_credentials_exception("Invalid username or password")

    if not user.is_verified:
        return LoginResponse(
            success=False,
            message="Please verify your email first",
        )

    if user.is_two_factor_enabled:
        statement = select(TwoFactorConfirmation).where(
            TwoFactorConfirmation.user_id == user.id
        )
        two_factor_confirmation = session.exec(statement).all()

        if len(two_factor_confirmation) == 0:
            statement = select(TwoFactorToken).where(TwoFactorToken.user_id == user.id)
            two_factor_tokens = session.exec(statement).all()
            if len(two_factor_tokens) > 0:
                for token in two_factor_tokens:
                    session.delete(token)
                session.commit()
            token = generate_two_factor_token()
            expires = datetime.now(timezone.utc) + timedelta(minutes=10)

            # Save token to database
            two_factor_token = TwoFactorToken(
                token=token, expires=expires, user_id=user.id
            )
            session.add(two_factor_token)
            session.commit()

            # Send token via email
            await send_two_factor_email(user.email, token)

            return LoginResponse(
                success=True,
                message="2FA code sent to your email",
            )

        expired_confirmations = [
            conf for conf in two_factor_confirmation if datetime.now() > conf.expires
        ]
        valid_confirmations = [
            conf for conf in two_factor_confirmation if datetime.now() <= conf.expires
        ]
        if expired_confirmations and len(valid_confirmations) == 0:
            for conf in expired_confirmations:
                session.delete(conf)
            session.commit()
            return LoginResponse(
                success=False,
                message="2FA code confirmation has expired, please login again",
            )

        # Clean up all confirmations
        for conf in two_factor_confirmation:
            session.delete(conf)
        session.commit()

    # Generate tokens
    access_token = create_access_token(
        {"sub": user.email}, timedelta(minutes=float(str(EXPIRY_TIME)))
    )
    refresh_token = create_refresh_token(
        {"sub": user.email}, timedelta(days=int(str(REFRESH_TOKEN_EXPIRY_TIME)))
    )

    return LoginResponse(
        success=True,
        message="Login successful",
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
    )


@app.post("/token/refresh", response_model=Token)
async def refresh_token(
    old_refresh_token: str,
    session: Annotated[Session, Depends(get_session)],
):
    user = validate_refresh_token(old_refresh_token, session)
    if not user:
        raise create_credentials_exception("Invalid credentials")
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
