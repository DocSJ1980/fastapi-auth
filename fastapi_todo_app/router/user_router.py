import secrets
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from fastapi_todo_app.db import get_session
from fastapi_todo_app.models.user_model import User
from fastapi_todo_app.models.verification_model import VerificationToken
from fastapi_todo_app.schemas.user_schema import (
    ChangePasswordRequest,
    Register_User,
    UpdateSettingsRequest,
    ResetPasswordRequest,
)
from fastapi_todo_app.schemas.verification_schema import VerificationResponse
from fastapi_todo_app.services.auth import (
    forgot_password_token,
    get_current_user,
    get_user_from_db,
    hash_password,
    verify_password,
    verify_reset_token,
    update_password,
)
from fastapi_todo_app.services.email_service import (
    send_forgot_password_email,
    send_verification_email,
)

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
        name=new_user.name,
        username=new_user.username,
        email=new_user.email,
        password=hash_password(new_user.password),
        is_verified=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    if not user.id:
        raise HTTPException(
            status_code=500, detail="Failed to persist user to the database"
        )

    # Create verification token
    token = secrets.token_urlsafe(32)
    verification_token = VerificationToken(token=token, user_id=user.id)
    session.add(verification_token)
    session.commit()

    # Send verification email
    send_verification_email(user.email, token)

    return {
        "message": f"User {user.username} registered successfully. Please check your email to verify your account."
    }


@user_router.get("/verify/{token}")
async def verify_email(token: str, session: Annotated[Session, Depends(get_session)]):
    verification = session.exec(
        select(VerificationToken).where(
            VerificationToken.token == token,
            VerificationToken.expires_at > datetime.now(),
        )
    ).first()

    if not verification:
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification token"
        )

    if verification.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification token has expired")

    user = session.exec(select(User).where(User.id == verification.user_id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    session.delete(verification)
    session.commit()

    return VerificationResponse(
        success=True, message="Email verified successfully", data={"email": user.email}
    )


@user_router.get("/me")
async def user_profile(current_user: Annotated[User, Depends(get_current_user)]):
    print("here")
    return current_user


@user_router.patch("/settings")
async def update_settings(
    request: UpdateSettingsRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: User = Depends(get_current_user),
):
    print(f"Request data: {request}")
    try:
        # Update user settings
        current_user.is_two_factor_enabled = request.is_two_factor_enabled
        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        return {"success": True, "message": "Settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@user_router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: User = Depends(get_current_user),
):
    try:
        # Verify current password
        if not verify_password(request.current_password, current_user.password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")

        # Update password
        current_user.password = hash_password(request.new_password)
        session.add(current_user)
        session.commit()

        return {"success": True, "message": "Password changed successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@user_router.post("/forgot-password")
async def forgot_password(
    email: str,
    session: Annotated[Session, Depends(get_session)],
):
    user = get_user_from_db(session, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create verification token
    fg_pw_token = forgot_password_token(user.id, session)
    if not fg_pw_token:
        raise HTTPException(
            status_code=500, detail="Failed to generate forgot password token"
        )

    # Send forgot password email
    send_forgot_password_email(user.email, fg_pw_token.token)

    return {"message": "Forgot password email sent successfully"}


@user_router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    session: Annotated[Session, Depends(get_session)],
):
    """Reset user's password using the reset token."""
    user = verify_reset_token(request.token, session)
    if not user:
        raise HTTPException(
            status_code=400, detail="Invalid or expired reset token"
        )

    if not update_password(user, request.new_password, session):
        raise HTTPException(
            status_code=500, detail="Failed to update password"
        )

    return {"message": "Password updated successfully"}
