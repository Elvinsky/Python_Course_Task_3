"""Tables owned by the Core service. Auth owns users; Core only stores the user id from the JWT."""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    price: Mapped[float]  # use Decimal / Numeric for real money
    stock: Mapped[int] = mapped_column(default=0)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        index=True
    )  # id from the JWT `sub` claim, no foreign key to Auth
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    quantity: Mapped[int]
