from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class VerifyOtpIn(BaseModel):
    email: EmailStr
    code: str = Field(pattern=r"^\d{6}$")


class UserOut(BaseModel):
    """Never include the password or its hash in a response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: str
    is_verified: bool


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105 - the OAuth2 token type, not a secret
