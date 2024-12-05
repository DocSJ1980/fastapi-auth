from typing import Annotated
import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from fastapi_todo_app.services.auth import (
    get_current_user,
    get_user_from_db,
    hash_password,
)
from fastapi_todo_app.db import get_session
from fastapi_todo_app.models.user_model import User
from fastapi_todo_app.models.verification_model import VerificationToken
from fastapi_todo_app.schemas.user_schema import Register_User
from fastapi_todo_app.services.email_service import send_verification_email
from fastapi_todo_app.schemas.verification_schema import VerificationResponse

user_router = APIRouter(
    prefix="/user", tags=["user"], responses={404: {"description": "Not found"}}
)


@user_router.get("/")
async def read_user():
    return {"message": "Welcome to FastAPI todo app User Page"}


@user_router.post("/register")
async def regiser_user(
    new_user: Annotated[Register_User, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    db_user = get_user_from_db(session, new_user.username, new_user.email)
    if db_user:
        raise HTTPException(
            status_code=409, detail="User with these credentials already exists"
        )
    user = User(
        username=new_user.username,
        email=new_user.email,
        password=hash_password(new_user.password),
        is_verified=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Create verification token
    token = secrets.token_urlsafe(32)
    verification_token = VerificationToken(
        token=token,
        user_id=user.id
    )
    session.add(verification_token)
    session.commit()
    
    # Send verification email
    send_verification_email(user.email, token)
    
    return {"message": f"User {user.username} registered successfully. Please check your email to verify your account."}


@user_router.get("/verify/{token}")
async def verify_email(token: str, session: Annotated[Session, Depends(get_session)]):
    verification = session.query(VerificationToken).filter(
        VerificationToken.token == token,
        VerificationToken.is_used == False
    ).first()
    
    if not verification:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    if verification.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification token has expired")
    
    user = session.query(User).filter(User.id == verification.user_id).first()
    user.is_verified = True
    
    # Delete the verification token instead of marking it as used
    session.delete(verification)
    session.commit()
    
    return VerificationResponse(
            success=True,
            message="Email verified successfully",
            data={"email": user.email}
        )


@user_router.get("/me")
async def user_profile(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
