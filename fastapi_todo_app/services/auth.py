from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from fastapi_todo_app.db import get_session
from fastapi_todo_app.models.user_model import User
from fastapi_todo_app.schemas.user_schema import RefreshTokenData, TokenData
from fastapi_todo_app.settings import (
    ALGORITHM,
    EXPIRY_TIME,
    REFRESH_TOKEN_EXPIRY_TIME,
    SECRET_KEY,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password, hash_password):
    return pwd_context.verify(password, hash_password)


def get_user_from_db(
    session: Annotated[Session, Depends(get_session)],
    username: str | None = None,
    email: str | None = None,
):
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        if user:
            return user

    return user


def authenticate_user(
    username, password, session: Annotated[Session, Depends(get_session)]
):
    db_user = get_user_from_db(session, username)
    if not db_user:
        return False
    if not verify_password(password, db_user.password):
        return False
    return db_user


def create_access_token(data: dict, expiry_time: timedelta | None):
    data_to_encode = data.copy()
    if expiry_time:
        expire = datetime.now(timezone.utc) + expiry_time
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=int(str(EXPIRY_TIME)))
    data_to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(data_to_encode, str(SECRET_KEY), algorithm=str(ALGORITHM))
    return encoded_jwt


def create_refresh_token(data: dict, expiry_time: timedelta | None):
    data_to_encode = data.copy()
    if expiry_time:
        expire = datetime.now(timezone.utc) + expiry_time
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=int(str(REFRESH_TOKEN_EXPIRY_TIME))
        )
    data_to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(data_to_encode, str(SECRET_KEY), algorithm=str(ALGORITHM))
    return encoded_jwt


def validate_refresh_token(
    token: str,
    session: Annotated[Session, Depends(get_session)],
):
    try:
        payload = jwt.decode(token, str(SECRET_KEY), str(ALGORITHM))
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = RefreshTokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user_from_db(session, email=token_data.email)
    if not user:
        raise credentials_exception
    return user


def get_current_user(
    token: Annotated[str, Depends(oauth_scheme)],
    session: Annotated[Session, Depends(get_session)],
):
    try:
        payload = jwt.decode(token, str(SECRET_KEY), str(ALGORITHM))
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_from_db(session, username=token_data.username)
    if not user:
        raise credentials_exception
    return user
