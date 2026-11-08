"""One-time codes stored in Redis (AC 1).

Contract used by the acceptance tests:
- key `otp:{email}`, value = a 6-digit string, TTL = settings.otp_ttl_seconds
- the code is never returned by the HTTP API
- a successful verification deletes the key, so a code works exactly once
"""

from redis.asyncio import Redis


async def issue_otp(redis: Redis, email: str, ttl_seconds: int) -> str:
    """Create, store (with TTL) and return a 6-digit code (hint: secrets.randbelow)."""
    # TODO (AC 1): generate with the `secrets` module, store under otp:{email} with an expiry.
    raise NotImplementedError("TODO (AC 1): implement issue_otp")


async def verify_otp(redis: Redis, email: str, code: str) -> bool:
    """Return True and delete the key when `code` is correct; otherwise return False."""
    # TODO (AC 1): compare in constant time (secrets.compare_digest), delete on success.
    raise NotImplementedError("TODO (AC 1): implement verify_otp")
