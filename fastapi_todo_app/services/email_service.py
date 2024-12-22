import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi_todo_app.services.auth import generate_two_factor_token
from fastapi_todo_app.settings import (
    FRONTEND_URL,
    SMTP_FROM_EMAIL,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USER,
)


def send_verification_email(to_email: str, token: str):
    msg = MIMEMultipart()
    msg["From"] = str(SMTP_FROM_EMAIL)
    msg["To"] = to_email
    msg["Subject"] = "Verify your email address"

    verification_link = f"{FRONTEND_URL}/auth/new-verification?token={token}"
    body = f"""
    Hello!
    
    Thank you for registering. Please click the link below to verify your email address:
    
    {verification_link}
    
    This link will expire in 24 hours.
    
    If you didn't register for an account, you can safely ignore this email.
    """

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(str(SMTP_HOST), int(SMTP_PORT))
        server.starttls()
        server.login(str(SMTP_USER), str(SMTP_PASSWORD))
        text = msg.as_string()
        server.sendmail(str(SMTP_FROM_EMAIL), to_email, text)
        server.quit()
        return True
    except Exception as e:
        return False


def send_forgot_password_email(to_email: str, token: str):
    msg = MIMEMultipart()
    msg["From"] = str(SMTP_FROM_EMAIL)
    msg["To"] = to_email
    msg["Subject"] = "Forgot Password"

    verification_link = f"{FRONTEND_URL}/auth/new-password?token={token}"
    body = f"""
    Hello!
    
    Thank you for your request. Please click the link below to reset your password:
    
    {verification_link}
    
    This link will expire in 24 hours.
    
    If you didn't request for a password reset, you can safely ignore this email.
    """

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(str(SMTP_HOST), int(SMTP_PORT))
        server.starttls()
        server.login(str(SMTP_USER), str(SMTP_PASSWORD))
        text = msg.as_string()
        server.sendmail(str(SMTP_FROM_EMAIL), to_email, text)
        server.quit()
        return True
    except Exception as e:
        return False


async def send_two_factor_email(email: str, token: str):
    """Send 2FA token via email"""
    msg = MIMEMultipart()
    msg["From"] = str(SMTP_FROM_EMAIL)
    msg["To"] = email
    msg["Subject"] = "Your Two-Factor Authentication Token"

    body = f"""
    Hello!
    
    Your two-factor authentication token is: {token}
    
    This token is valid for a short period of time. Please use it to complete your login process.
    
    If you did not request this token, please ignore this email.
    """

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(str(SMTP_HOST), int(SMTP_PORT))
        server.starttls()
        server.login(str(SMTP_USER), str(SMTP_PASSWORD))
        text = msg.as_string()
        server.sendmail(str(SMTP_FROM_EMAIL), email, text)
        server.quit()
        return True
    except Exception as e:
        return False
