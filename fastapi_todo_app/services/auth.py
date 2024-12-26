import random
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from fastapi_todo_app.db import get_session
from fastapi_todo_app.models.forgot_password import ForgotPasswordModel
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


def create_credentials_exception(detail: str, headers: dict | None = None):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers=headers or {"WWW-Authenticate": "Bearer"},
    )


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password, hash_password):
    return pwd_context.verify(password, hash_password)


def get_user_from_db(
    session: Session,
    username: str | None = None,
    email: str | None = None,
):
    print(f"🔍 Searching for user with username: {username}, email: {email}")
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    print(f"👤 User found by username: {user is not None}")
    if not user and email:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        print(f"👤 User found by email: {user is not None}")
        if user:
            return user
    return user


def authenticate_user(
    username, password, session: Annotated[Session, Depends(get_session)]
):
    print(f"🔐 Attempting to authenticate user: {username}")
    db_user = get_user_from_db(session, username)
    if not db_user:
        raise ValueError("User not found")
    if not verify_password(password, db_user.password):
        raise ValueError("Incorrect password")
    print(f"✅ Authentication successful for user: {username}")
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
        username: str | None = payload.get("sub")
        if email is None:
            raise create_credentials_exception("Token payload missing email field")
        token_data = RefreshTokenData(email=email, username=username)
    except JWTError:
        raise create_credentials_exception("Could not validate token")
    user = get_user_from_db(
        session, email=token_data.email, username=token_data.username
    )
    if not user:
        raise create_credentials_exception("Invalid credentials")
    return user


def get_current_user(
    token: Annotated[str, Depends(oauth_scheme)],
    session: Annotated[Session, Depends(get_session)],
):
    print(token)

    try:
        print("🚀 ~ file: auth.py:124 ~ token:", token, SECRET_KEY, ALGORITHM)
        try:
            payload = jwt.decode(token, str(SECRET_KEY), algorithms=[str(ALGORITHM)])
            print("🚀 ~ file: auth.py:124 ~ payload:", payload)
        except jwt.ExpiredSignatureError:
            raise create_credentials_exception(
                "Token has expired. Please refresh your token or login again."
            )
        except jwt.InvalidTokenError:
            raise create_credentials_exception("Invalid token format or signature.")
        except Exception as e:
            print(f"JWT decode error: {str(e)}")
            raise create_credentials_exception(f"Failed to decode token: {str(e)}")

        email: str | None = payload.get("sub")
        username: str | None = payload.get("sub")
        print(f"Email: {email}")
        print(f"Username: {username}")
        if username is None and email is None:
            raise create_credentials_exception("Token payload missing required fields")
        token_data = TokenData(username=username, email=email)
    except JWTError:
        raise create_credentials_exception("Could not validate token")

    user = get_user_from_db(
        session, email=token_data.email, username=token_data.username
    )
    if not user:
        raise create_credentials_exception("User not found")
    return user


def forgot_password_token(
    user_id: int, session: Annotated[Session, Depends(get_session)]
) -> ForgotPasswordModel:
    """Generate a forgot password token for a user."""
    # Delete any existing tokens for this user
    statement = select(ForgotPasswordModel).where(
        ForgotPasswordModel.user_id == user_id
    )
    existing_tokens = session.exec(statement).all()
    for token in existing_tokens:
        session.delete(token)
    session.commit()

    # Create new token
    token = secrets.token_urlsafe(32)
    forgot_password_token = ForgotPasswordModel(
        token=token,
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    session.add(forgot_password_token)
    session.commit()
    session.refresh(forgot_password_token)
    return forgot_password_token


def verify_reset_token(token: str, session: Session) -> User | None:
    """Verify the reset token and return the associated user."""
    statement = select(ForgotPasswordModel).where(ForgotPasswordModel.token == token)
    reset_token = session.exec(statement).first()

    if not reset_token:
        return None

    # Check if token is expired
    if datetime.now(timezone.utc) > reset_token.expires_at:
        session.delete(reset_token)
        session.commit()
        return None

    statement = select(User).where(User.id == reset_token.user_id)
    user = session.exec(statement).first()

    if user:
        session.delete(reset_token)
        session.commit()

    return user


def update_password(user: User, new_password: str, session: Session) -> bool:
    """Update user's password with the new one."""
    try:
        user.password = hash_password(new_password)
        session.add(user)
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False


def generate_two_factor_token() -> str:
    """Generate a 6-digit 2FA token"""
    return "".join(random.choices("0123456789", k=6))
