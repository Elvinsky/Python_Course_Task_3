"""AC 4: RBAC. `user` places orders; `moderator` and `admin` override prices and edit stock."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Item, Order
from tests.conftest import MakeToken


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize(("role", "expected"), [("user", 403), ("moderator", 200), ("admin", 200)])
async def test_price_override_matrix(
    client: AsyncClient, make_token: MakeToken, item: Item, role: str, expected: int
) -> None:
    response = await client.patch(
        f"/api/items/{item.id}/price", json={"price": 12.5}, headers=bearer(make_token(role=role))
    )
    assert response.status_code == expected, response.text
    if expected == 200:
        assert response.json()["price"] == 12.5


@pytest.mark.parametrize(("role", "expected"), [("user", 403), ("moderator", 200), ("admin", 200)])
async def test_stock_edit_matrix(
    client: AsyncClient, make_token: MakeToken, item: Item, role: str, expected: int
) -> None:
    response = await client.patch(
        f"/api/items/{item.id}/stock", json={"stock": 42}, headers=bearer(make_token(role=role))
    )
    assert response.status_code == expected, response.text
    if expected == 200:
        assert response.json()["stock"] == 42


@pytest.mark.parametrize(("role", "expected"), [("user", 201), ("moderator", 403), ("admin", 403)])
async def test_order_placement_matrix(
    client: AsyncClient, make_token: MakeToken, item: Item, role: str, expected: int
) -> None:
    response = await client.post(
        "/api/orders",
        json={"item_id": item.id, "quantity": 1},
        headers=bearer(make_token(role=role)),
    )
    assert response.status_code == expected, response.text


async def test_unauthenticated_requests_are_401_not_403(client: AsyncClient, item: Item) -> None:
    assert (
        await client.post("/api/orders", json={"item_id": item.id, "quantity": 1})
    ).status_code == 401
    assert (await client.patch(f"/api/items/{item.id}/price", json={"price": 1})).status_code == 401


async def test_price_change_is_persisted(
    client: AsyncClient, make_token: MakeToken, item: Item, db_session: AsyncSession
) -> None:
    await client.patch(
        f"/api/items/{item.id}/price",
        json={"price": 99.0},
        headers=bearer(make_token(role="admin")),
    )
    row = (await db_session.execute(select(Item).where(Item.id == item.id))).scalar_one()
    await db_session.refresh(row)
    assert row.price == 99.0


async def test_unknown_item_is_404(client: AsyncClient, make_token: MakeToken) -> None:
    headers = bearer(make_token(role="moderator"))
    assert (
        await client.patch("/api/items/999/price", json={"price": 1}, headers=headers)
    ).status_code == 404
    assert (
        await client.patch("/api/items/999/stock", json={"stock": 1}, headers=headers)
    ).status_code == 404


@pytest.mark.parametrize("payload", [{"price": -1}, {"price": 0}, {}])
async def test_invalid_price_is_422(
    client: AsyncClient, make_token: MakeToken, item: Item, payload: dict[str, float]
) -> None:
    response = await client.patch(
        f"/api/items/{item.id}/price", json=payload, headers=bearer(make_token(role="admin"))
    )
    assert response.status_code == 422


async def test_order_decrements_stock_and_records_the_user(
    client: AsyncClient, make_token: MakeToken, item: Item, db_session: AsyncSession
) -> None:
    response = await client.post(
        "/api/orders",
        json={"item_id": item.id, "quantity": 2},
        headers=bearer(make_token(role="user", user_id=7)),
    )
    assert response.status_code == 201, response.text
    assert response.json()["user_id"] == 7 and response.json()["quantity"] == 2
    row = (await db_session.execute(select(Item).where(Item.id == item.id))).scalar_one()
    await db_session.refresh(row)
    assert row.stock == 3
    assert (await db_session.execute(select(Order))).scalars().one().user_id == 7


async def test_order_with_insufficient_stock_is_409_and_changes_nothing(
    client: AsyncClient, make_token: MakeToken, item: Item, db_session: AsyncSession
) -> None:
    response = await client.post(
        "/api/orders",
        json={"item_id": item.id, "quantity": 6},
        headers=bearer(make_token(role="user")),
    )
    assert response.status_code == 409
    row = (await db_session.execute(select(Item).where(Item.id == item.id))).scalar_one()
    await db_session.refresh(row)
    assert row.stock == 5
    assert (await db_session.execute(select(Order))).first() is None


async def test_order_for_unknown_item_is_404_and_zero_quantity_is_422(
    client: AsyncClient, make_token: MakeToken, item: Item
) -> None:
    headers = bearer(make_token(role="user"))
    assert (
        await client.post("/api/orders", json={"item_id": 999, "quantity": 1}, headers=headers)
    ).status_code == 404
    assert (
        await client.post("/api/orders", json={"item_id": item.id, "quantity": 0}, headers=headers)
    ).status_code == 422
