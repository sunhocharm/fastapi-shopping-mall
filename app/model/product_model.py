from datetime import datetime, UTC
from pydantic import AwareDatetime
from sqlalchemy_utc import UtcDateTime
from sqlmodel import SQLModel, Field, Relationship, func


class Category(SQLModel, table=True):
    """카테고리 테이블"""
    __tablename__ = "categories"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    slug: str = Field(unique=True)
    description: str
    is_active: bool | None = Field(default=True)
    sort_order: int | None = Field(default=0)

    created_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now()})
    updated_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now(), "onupdate": lambda: datetime.now(tz=UTC)})

    # relationships
    products: list["Product"] = Relationship(back_populates="category")


class Product(SQLModel, table=True):
    """상품 테이블"""
    __tablename__ = "products"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    slug: str
    description: str
    price: int                          # 원 단위
    original_price: int | None = None   # 원래 가격 (할인 계산용)
    stock: int | None = Field(default=0)
    is_active: bool | None = Field(default=True)
    is_featured: bool | None = Field(default=False)  # 추천 상품

    # foreign keys
    category_id: int | None = Field(default=None, foreign_key="categories.id", nullable=True)

    created_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now()})
    updated_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now(), "onupdate": lambda: datetime.now(tz=UTC)})

    # relationships
    category: Category = Relationship(back_populates="products")
    images: list["ProductImage"] = Relationship(back_populates="product")

    @property
    def discount_percent(self) -> int | None:
        """할인율 계산"""
        if self.original_price and self.original_price > self.price:
            return int((1 - self.price / self.original_price) * 100)
        return None

    @property
    def main_image(self) -> str:
        """대표 이미지"""
        if self.images:
            return self.images[0].url
        return "/static/images/no-image.png"


class ProductImage(SQLModel, table=True):
    """상품 이미지 테이블"""
    __tablename__ = "product_images"

    id: int | None = Field(default=None, primary_key=True)
    url: str
    thumb_url: str | None = Field(default=None)
    alt: str | None = None
    sort_order: int | None = Field(default=0)

    # foreign keys
    product_id: int = Field(foreign_key="products.id")

    created_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now()})
    updated_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now(), "onupdate": lambda: datetime.now(tz=UTC)})

    # relationships
    product: Product = Relationship(back_populates="images")
