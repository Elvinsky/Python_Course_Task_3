"""Order endpoints, mounted under /api.

POST /api/orders   role `user` only (moderators and admins get 403)
201 OrderOut, 404 unknown item, 409 not enough stock (stock stays unchanged), 422 invalid body.
A successful order decrements the item's stock.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import DbSession
from app.models import Order
from app.schemas import OrderIn, OrderOut
from app.security import CurrentUser, require_roles

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=OrderOut)
async def place_order(
    payload: OrderIn,
    db: DbSession,
    user: Annotated[CurrentUser, Depends(require_roles("user"))],
) -> Order:
    # TODO (AC 4): check the item and the stock, decrement it, store the order for `user.id`.
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "TODO (AC 4): implement order placement")
