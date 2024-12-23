from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    print("Warning: No .env file found")
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret)
TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)
SECRET_KEY = config("SECRET_KEY", cast=Secret)
ALGORITHM = config("ALGORITHM", cast=Secret)
EXPIRY_TIME = config("EXPIRY_TIME", cast=Secret)
REFRESH_TOKEN_EXPIRY_TIME = config("REFRESH_TOKEN_EXPIRY_TIME", cast=Secret)
EMAIL_VERIFICATION_TOKEN_EXPIRY_TIME = config(
    "EMAIL_VERIFICATION_TOKEN_EXPIRY_TIME", cast=int
)
# SMTP Settings
SMTP_HOST = config("SMTP_HOST", cast=str)
SMTP_PORT = config("SMTP_PORT", cast=int)
SMTP_USER = config("SMTP_USER", cast=str)
SMTP_PASSWORD = config("SMTP_PASSWORD", cast=Secret)
SMTP_FROM_EMAIL = config("SMTP_FROM_EMAIL", cast=str)

# Frontend URL for email verification
FRONTEND_URL = config("FRONTEND_URL", cast=str, default="http://localhost:3000")
