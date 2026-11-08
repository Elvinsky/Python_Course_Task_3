"""AC 1: registration, password hashing and Redis OTP verification."""

from fakeredis import FakeAsyncRedis
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import User
from app.security import hash_password, verify_password
from tests.acceptance.helpers import PASSWORD, current_otp, register


async def test_register_creates_an_unverified_user_without_leaking_secrets(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    response = await register(client)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert body["role"] == "user"
    assert body["is_verified"] is False
    assert PASSWORD not in response.text
    assert "password" not in body and "password_hash" not in body

    user = (await db_session.execute(select(User))).scalar_one()
    assert user.is_verified is False and user.role == "user"


async def test_password_is_stored_as_an_argon2id_hash(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await register(client)
    user = (await db_session.execute(select(User))).scalar_one()
    assert user.password_hash != PASSWORD
    assert user.password_hash.startswith("$argon2id$"), "hash passwords with Argon2id"


def test_hashing_is_salted_and_verifiable() -> None:
    first, second = hash_password("s3cret-value"), hash_password("s3cret-value")
    assert first != second, "hashes must be salted"
    assert verify_password("s3cret-value", first) is True
    assert verify_password("another-value", first) is False


async def test_duplicate_email_is_rejected(client: AsyncClient) -> None:
    assert (await register(client)).status_code == 201
    assert (await register(client)).status_code == 409


async def test_short_password_is_rejected(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/register", json={"email": "bob@example.com", "password": "short"}
    )
    assert response.status_code == 422


async def test_otp_is_stored_in_redis_with_a_ttl_and_never_returned(
    client: AsyncClient, redis_client: FakeAsyncRedis
) -> None:
    response = await register(client)
    code = await current_otp(redis_client)
    assert len(code) == 6 and code.isdigit()
    assert code not in response.text, "the OTP must never be returned by the API"
    ttl = await redis_client.ttl("otp:alice@example.com")
    assert 0 < ttl <= get_settings().otp_ttl_seconds


async def test_correct_otp_verifies_the_user_and_is_single_use(
    client: AsyncClient, redis_client: FakeAsyncRedis, db_session: AsyncSession
) -> None:
    await register(client)
    code = await current_otp(redis_client)
    payload = {"email": "alice@example.com", "code": code}

    first = await client.post("/auth/verify-otp", json=payload)
    assert first.status_code == 200, first.text
    assert first.json()["is_verified"] is True
    assert await redis_client.get("otp:alice@example.com") is None, "delete the code after use"

    second = await client.post("/auth/verify-otp", json=payload)
    assert second.status_code in {400, 401}

    user = (await db_session.execute(select(User))).scalar_one()
    await db_session.refresh(user)
    assert user.is_verified is True


async def test_wrong_otp_is_rejected_and_the_user_stays_unverified(
    client: AsyncClient, redis_client: FakeAsyncRedis, db_session: AsyncSession
) -> None:
    await register(client)
    real = await current_otp(redis_client)
    wrong = "000000" if real != "000000" else "111111"
    response = await client.post(
        "/auth/verify-otp", json={"email": "alice@example.com", "code": wrong}
    )
    assert response.status_code in {400, 401}
    user = (await db_session.execute(select(User))).scalar_one()
    assert user.is_verified is False


async def test_expired_otp_is_rejected(client: AsyncClient, redis_client: FakeAsyncRedis) -> None:
    await register(client)
    code = await current_otp(redis_client)
    await redis_client.delete("otp:alice@example.com")  # what Redis does when the TTL runs out
    response = await client.post(
        "/auth/verify-otp", json={"email": "alice@example.com", "code": code}
    )
    assert response.status_code in {400, 401}
