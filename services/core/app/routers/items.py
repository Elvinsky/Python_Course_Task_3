"""Item endpoints, mounted under /api.

GET   /api/items                    any authenticated user
PATCH /api/items/{item_id}/price    moderator or admin
PATCH /api/items/{item_id}/stock    moderator or admin
404 for an unknown item, 422 for an invalid body.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.deps import DbSession
from app.models import Item
from app.schemas import ItemOut, PriceUpdate, StockUpdate
from app.security import CurrentUser, get_current_user, require_roles

router = APIRouter(prefix="/items", tags=["items"])

Staff = Depends(require_roles("moderator", "admin"))


@router.get("", response_model=list[ItemOut])
async def list_items(
    db: DbSession, user: Annotated[CurrentUser, Depends(get_current_user)]
) -> list[Item]:
    """Worked example: the handler stays free of auth code, the guard does the work."""
    result = await db.scalars(select(Item).order_by(Item.id))
    return list(result.all())


@router.patch("/{item_id}/price", response_model=ItemOut, dependencies=[Staff])
async def override_price(item_id: int, payload: PriceUpdate, db: DbSession) -> Item:
    # TODO (AC 4): load the item (404 if missing), set the price, commit, return it.
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "TODO (AC 4): implement price override")


@router.patch("/{item_id}/stock", response_model=ItemOut, dependencies=[Staff])
async def edit_stock(item_id: int, payload: StockUpdate, db: DbSession) -> Item:
    # TODO (AC 4): load the item (404 if missing), set the stock, commit, return it.
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "TODO (AC 4): implement stock edit")
