import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
        print(f"Failed to send email: {str(e)}")
        return False


def send_forgot_password_email(to_email: str, token: str):
    msg = MIMEMultipart()
    msg["From"] = str(SMTP_FROM_EMAIL)
    msg["To"] = to_email
    msg["Subject"] = "Forgot Password"

    verification_link = f"{FRONTEND_URL}/auth/forgot-pw-verification?token={token}"
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
        print(f"Failed to send email: {str(e)}")
        return False
