"""Password hashing and access tokens (AC 1, AC 2).

Contract used by the acceptance tests:
- passwords are hashed with Argon2id (hashes start with "$argon2id$"), salted, never returned or logged
- the access token is a signed JWT with claims: sub (the user id as a *string*), role, exp
"""

from app.config import Settings


def hash_password(password: str) -> str:
    """Return an Argon2id hash of `password` (hint: argon2.PasswordHasher)."""
    # TODO (AC 1): hash with Argon2id.
    raise NotImplementedError("TODO (AC 1): implement hash_password")


def verify_password(password: str, password_hash: str) -> bool:
    """Return True when `password` matches `password_hash`; never raise on a mismatch."""
    # TODO (AC 1): verify with Argon2 and return False on mismatch.
    raise NotImplementedError("TODO (AC 1): implement verify_password")


def create_access_token(user_id: int, role: str, settings: Settings) -> str:
    """Return a signed JWT bearer token with the claims sub, role and exp."""
    # TODO (AC 2): sign a JWT with settings.jwt_secret.get_secret_value() and settings.jwt_algorithm;
    # exp = now + settings.access_token_ttl_seconds.
    raise NotImplementedError("TODO (AC 2): implement create_access_token")
