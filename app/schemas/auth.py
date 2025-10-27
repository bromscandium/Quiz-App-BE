from pydantic import EmailStr

from app.schemas.user import Base


class LoginRequest(Base):
    email: EmailStr
    password: str


class TokenRequest(Base):
    refresh_token: str


class TokenResponse(Base):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int | None = None
