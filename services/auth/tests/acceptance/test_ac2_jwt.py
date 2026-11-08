"""AC 2: signed JWT bearer tokens are issued upon authentication."""

import time

import jwt
from fakeredis import FakeAsyncRedis
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import User
from tests.acceptance.helpers import login, register, register_and_verify


async def test_login_returns_a_signed_bearer_token(
    client: AsyncClient, redis_client: FakeAsyncRedis, db_session: AsyncSession
) -> None:
    await register_and_verify(client, redis_client)
    response = await login(client)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["token_type"].lower() == "bearer"

    settings = get_settings()
    claims = jwt.decode(
        body["access_token"],
        settings.jwt_secret.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
    )
    user = (await db_session.execute(select(User))).scalar_one()
    assert claims["sub"] == str(user.id), "sub must be the user id as a string"
    assert claims["role"] == "user"
    now = time.time()
    assert now < claims["exp"] <= now + settings.access_token_ttl_seconds + 5


async def test_token_signed_with_another_key_is_not_valid(
    client: AsyncClient, redis_client: FakeAsyncRedis
) -> None:
    await register_and_verify(client, redis_client)
    token = (await login(client)).json()["access_token"]
    try:
        jwt.decode(token, "a-completely-different-key-of-sufficient-length", algorithms=["HS256"])
    except jwt.InvalidSignatureError:
        return
    raise AssertionError("the token must be signed with JWT_SECRET")


async def test_wrong_password_is_unauthorized(
    client: AsyncClient, redis_client: FakeAsyncRedis
) -> None:
    await register_and_verify(client, redis_client)
    assert (await login(client, attempt="not the password")).status_code == 401


async def test_unknown_user_is_unauthorized(client: AsyncClient) -> None:
    assert (await login(client, email="nobody@example.com")).status_code == 401


async def test_unverified_user_cannot_log_in(client: AsyncClient) -> None:
    await register(client)
    assert (await login(client)).status_code == 403
