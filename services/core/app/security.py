"""JWT validation and role guards (AC 3, AC 4, AC 8).

Core validates tokens LOCALLY with the shared key: it never calls the Auth service.

Contract used by the acceptance tests:
- missing token, malformed token, wrong signature, expired token, or a token without
  `sub` / `role` -> 401 with the header `WWW-Authenticate: Bearer`
- authenticated but not allowed (wrong role) -> 403
"""

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# Tokens are issued by the Auth service at /auth/login.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class CurrentUser(BaseModel):
    id: int
    role: str  # "admin" | "moderator" | "user"


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> CurrentUser:
    """Decode and validate the bearer token and return the user it describes."""
    # TODO (AC 3): decode with jwt.decode(token, settings.jwt_secret.get_secret_value(),
    # algorithms=[settings.jwt_algorithm]) (never trust the token's own `alg` header), require the
    # `sub`, `role` and `exp` claims, and turn every jwt.PyJWTError into the 401 described above.
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "TODO (AC 3): implement get_current_user")


def require_roles(*allowed: str) -> Callable[..., Awaitable[CurrentUser]]:
    """Build a dependency that only lets users with one of the `allowed` roles through."""

    async def guard(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        # TODO (AC 4): raise 403 when user.role is not in `allowed`, otherwise return the user.
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "TODO (AC 4): implement require_roles")

    return guard
