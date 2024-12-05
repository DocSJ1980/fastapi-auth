import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi_todo_app.settings import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    SMTP_FROM_EMAIL,
    FRONTEND_URL
)

def send_verification_email(to_email: str, token: str):
    msg = MIMEMultipart()
    msg['From'] = str(SMTP_FROM_EMAIL)
    msg['To'] = to_email
    msg['Subject'] = "Verify your email address"
    
    verification_link = f"{FRONTEND_URL}/verify-email?token={token}"
    body = f"""
    Hello!
    
    Thank you for registering. Please click the link below to verify your email address:
    
    {verification_link}
    
    This link will expire in 24 hours.
    
    If you didn't register for an account, you can safely ignore this email.
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
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
