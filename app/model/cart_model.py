from datetime import datetime, UTC
from sqlalchemy_utc import UtcDateTime
from pydantic import AwareDatetime
from sqlmodel import SQLModel, Field, Relationship, func


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.model.user_model import User
    from app.model.product_model import Product


class Cart(SQLModel, table=True):
    """장바구니 테이블"""
    __tablename__ = "carts"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="users.id", unique=True, nullable=True) # 비회원인 경우 null 가능
    session_id: str = Field(unique=True, nullable=False)  # 비회원용, 회원 모두 있어야 한다.

    created_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now()})
    updated_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now(), "onupdate": lambda: datetime.now(tz=UTC)})

    # 관계
    user: "User" = Relationship()
    items: list["CartItem"] = Relationship(back_populates="cart", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    @property
    def total_price(self) -> int:
        """총 금액"""
        return sum(item.subtotal for item in self.items)

    @property
    def total_quantity(self) -> int:
        """총 수량"""
        return sum(item.quantity for item in self.items)


class CartItem(SQLModel, table=True):
    """장바구니 상품 테이블"""
    __tablename__ = "cart_items"

    id: int | None = Field(default=None, primary_key=True)
    cart_id: int = Field(foreign_key="carts.id", nullable=False)
    product_id: int = Field(foreign_key="products.id", nullable=False)
    quantity: int = Field(default=1, ge=1)

    created_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now()})

    # 관계
    cart: Cart = Relationship(back_populates="items")
    product: "Product" = Relationship()

    @property
    def subtotal(self) -> int:
        """소계"""
        return self.product.price * self.quantity
