from sqlmodel import SQLModel, Field


class OrderCreate(SQLModel):
    # 배송 정보
    recipient: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    zipcode: str = Field(max_length=10)
    address1: str = Field(max_length=200)
    address2: str | None = Field(default=None, max_length=200)
    memo: str | None = Field(default=None)  # 배송 메모

    save_address: bool | None = Field(default=False)


# class OrderItem(SQLModel, table=True):
#     """주문 상품 테이블"""
#     __tablename__ = "order_items"

#     id: int | None = Field(default=None, primary_key=True)

#     # foreign keys
#     order_id: int = Field(foreign_key="orders.id")
#     product_id: int = Field(foreign_key="products.id")

#     # 주문 당시 정보 (상품 정보가 변경되어도 주문 내역은 유지)
#     product_name: str
#     product_price: int
#     quantity: int
#     subtotal: int

#     created_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now()})
#     updated_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now(), "onupdate": lambda: datetime.now(tz=UTC)})

#     # relationships
#     order: Order = Relationship(back_populates="items")
#     product: "Product" = Relationship()
