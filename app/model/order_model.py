from datetime import datetime, UTC
from sqlalchemy_utc import UtcDateTime
from pydantic import AwareDatetime

from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, func
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.model.user_model import User
    from app.model.product_model import Product
    from app.model.payment_model import Payment


class OrderStatus(str, Enum):
    """주문 상태"""
    PENDING = "pending"           # 결제 대기
    PAID = "paid"                 # 결제 완료
    PREPARING = "preparing"       # 배송 준비
    SHIPPING = "shipping"         # 배송 중
    DELIVERED = "delivered"       # 배송 완료
    CANCELLED = "cancelled"       # 취소


class Order(SQLModel, table=True):
    """주문 테이블"""
    __tablename__ = "orders"

    id: int | None = Field(default=None, primary_key=True)
    order_number: str = Field(unique=True)  # 주문번호

    # foreign keys
    user_id: int = Field(foreign_key="users.id")

    # 주문 정보
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    total_price: int  # 상품 금액
    shipping_fee: int = Field(default=0)  # 배송비
    final_price: int  # 최종 결제 금액

    # 배송 정보
    recipient: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    zipcode: str = Field(max_length=10)
    address1: str = Field(max_length=200)
    address2: str | None = Field(default=None, max_length=200)
    memo: str | None = Field(default=None)  # 배송 메모

    # 시간
    paid_at: datetime | None = Field(default=None)
    shipped_at: datetime | None = Field(default=None)
    delivered_at: datetime | None = Field(default=None)
    cancelled_at: datetime | None = Field(default=None)

    created_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now()})
    updated_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now(), "onupdate": lambda: datetime.now(tz=UTC)})

    # relationships
    user: "User" = Relationship(back_populates="orders")
    items: list["OrderItem"] = Relationship(back_populates="order", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    payment: "Payment" = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    """주문 상품 테이블"""
    __tablename__ = "order_items"

    id: int | None = Field(default=None, primary_key=True)

    # foreign keys
    order_id: int = Field(foreign_key="orders.id")
    product_id: int = Field(foreign_key="products.id")

    # 주문 당시 정보 (상품 정보가 변경되어도 주문 내역은 유지)
    product_name: str
    product_price: int
    quantity: int
    subtotal: int

    created_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now()})
    updated_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now(), "onupdate": lambda: datetime.now(tz=UTC)})

    # relationships
    order: Order = Relationship(back_populates="items")
    product: "Product" = Relationship()
