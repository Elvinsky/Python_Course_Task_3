"""AC 3: the security dependency in Core decodes and validates JWTs."""

import jwt
import pytest
from httpx import AsyncClient

from tests.conftest import MakeToken

URL = "/api/items"


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def test_missing_token_is_401_with_a_bearer_challenge(client: AsyncClient) -> None:
    response = await client.get(URL)
    assert response.status_code == 401
    assert response.headers["www-authenticate"].lower().startswith("bearer")


@pytest.mark.parametrize("token", ["garbage", "a.b.c", ""])
async def test_malformed_token_is_401(client: AsyncClient, token: str) -> None:
    response = await client.get(URL, headers=bearer(token))
    assert response.status_code == 401


async def test_expired_token_is_401(client: AsyncClient, make_token: MakeToken) -> None:
    response = await client.get(URL, headers=bearer(make_token(ttl=-10)))
    assert response.status_code == 401
    assert response.headers["www-authenticate"].lower().startswith("bearer")


async def test_token_signed_with_another_key_is_401(
    client: AsyncClient, make_token: MakeToken
) -> None:
    token = make_token(key="an-attacker-key-that-is-also-long-enough-123")
    assert (await client.get(URL, headers=bearer(token))).status_code == 401


async def test_unsigned_alg_none_token_is_401(client: AsyncClient) -> None:
    token = jwt.encode({"sub": "1", "role": "admin"}, key=None, algorithm="none")
    assert (await client.get(URL, headers=bearer(token))).status_code == 401


@pytest.mark.parametrize("missing", ["sub", "role", "exp"])
async def test_token_without_a_required_claim_is_401(
    client: AsyncClient, make_token: MakeToken, missing: str
) -> None:
    assert (await client.get(URL, headers=bearer(make_token(omit=(missing,))))).status_code == 401


@pytest.mark.parametrize("role", ["user", "moderator", "admin"])
async def test_valid_token_of_any_role_can_list_items(
    client: AsyncClient, make_token: MakeToken, role: str
) -> None:
    response = await client.get(URL, headers=bearer(make_token(role=role)))
    assert response.status_code == 200, response.text
    assert response.json() == []
