from pydantic import BaseModel

class VerificationResponse(BaseModel):
    success: bool
    message: str
    data: dict | None = None
