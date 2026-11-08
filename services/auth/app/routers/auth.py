"""Auth endpoints, mounted under /auth (see app/main.py).

POST /auth/register    201 UserOut          409 email already registered
POST /auth/verify-otp  200 UserOut          400 or 401 wrong/expired code
POST /auth/login       200 TokenOut         401 bad credentials, 403 account not verified
                       (OAuth2 password form: `username` is the email)

Log events (structlog, JSON) the acceptance tests look for:
user_registered, otp_issued, otp_verified, otp_failed, login_succeeded, login_failed.
Never log a password, a hash, an OTP code or a token.
"""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.config import get_settings
from app.deps import DbSession, RedisClient
from app.models import User
from app.schemas import RegisterIn, TokenOut, UserOut, VerifyOtpIn

router = APIRouter(tags=["auth"])
log = structlog.get_logger()


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def register(payload: RegisterIn, db: DbSession, redis: RedisClient) -> User:
    # TODO (AC 1, AC 6): reject duplicates (409), hash the password, store the user (role "user",
    # not verified), issue an OTP, log user_registered and otp_issued.
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "TODO (AC 1): implement registration")


@router.post("/verify-otp", response_model=UserOut)
async def verify_otp_endpoint(payload: VerifyOtpIn, db: DbSession, redis: RedisClient) -> User:
    # TODO (AC 1, AC 6): check the code, mark the user verified, log otp_verified / otp_failed.
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "TODO (AC 1): implement OTP verification")


@router.post("/login", response_model=TokenOut)
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession) -> TokenOut:
    settings = get_settings()
    # TODO (AC 2, AC 6): look up form.username, verify the password (401), require is_verified (403),
    # return create_access_token(...), log login_succeeded / login_failed.
    _ = settings
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "TODO (AC 2): implement login")
