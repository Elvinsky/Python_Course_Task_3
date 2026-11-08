"""Your own tests for the JWT guard and RBAC (AC 5). Use the `make_token` fixture from conftest.py.

Requirements, checked by tests/acceptance/test_ac5_learner_tests.py: at least 4 test functions that
together mention the status codes 401, 403 and 200 (for example in the test names or the asserts).
"""

from httpx import AsyncClient

from tests.conftest import MakeToken


async def test_missing_token_returns_401(client: AsyncClient) -> None:
    """Worked example. Add the rest of the guard matrix below."""
    assert (await client.get("/api/items")).status_code == 401


async def test_valid_token_can_list_items_returns_200(
    client: AsyncClient, make_token: MakeToken
) -> None:
    response = await client.get("/api/items", headers={"Authorization": f"Bearer {make_token()}"})
    assert response.status_code == 200


# TODO (AC 5): expired and tampered tokens -> 401
# TODO (AC 5): authenticated but wrong role -> 403 (user editing a price, moderator ordering)
# TODO (AC 5): allowed roles -> 200 (moderator and admin overriding a price; use the `item` fixture)
# Hint: `make_token(role="moderator")` returns a valid token; `make_token(ttl=-10)` an expired one.
