from pydantic import BaseModel, EmailStr, ConfigDict


class AuthBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class LoginRequest(AuthBase):
    email: EmailStr
    password: str


class TokenRequest(AuthBase):
    refresh_token: str


class TokenResponse(AuthBase):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int | None = None
