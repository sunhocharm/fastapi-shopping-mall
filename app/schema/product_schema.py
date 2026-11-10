from sqlmodel import SQLModel, Field


class CategoryCreate(SQLModel):
    name: str = Field(min_length=3, max_length=50)
    slug: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=10)
    is_active: bool | None = Field(default=True)
    sort_order: int | None = Field(default=0)


class CategoryUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=3, max_length=50)
    slug: str| None = Field(default=None, min_length=3, max_length=50)
    description: str | None = Field(default=None, min_length=10)
    is_active: bool | None = Field(default=True)
    sort_order: int | None = Field(default=0)


class CategoryResponse(SQLModel):
    name: str | None = Field(default=None)
    slug: str| None = Field(default=None)
    description: str | None = Field(default=None)
    is_active: bool | None = Field(default=True)
    sort_order: int | None = Field(default=0)

    model_config = {"from_attributes": True}


class ProductImageResponse(SQLModel):
    id: int
    url: str
    thumb_url: str | None = Field(default=None)
    alt: str | None
    sort_order: int
    product_id: int

    model_config = {"from_attributes": True}


class ProductCreate(SQLModel):
    """상품 생성"""
    name: str = Field(min_length=3, max_length=200)
    slug: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=3)
    price: int = Field(ge=0)  # 원 단위
    original_price: int | None = Field(default=None)  # 원래 가격 (할인 표시용)
    stock: int = Field(default=0, ge=0)
    is_active: bool | None = Field(default=True)
    is_featured: bool | None = Field(default=False)  # 추천 상품

    category_id: int


class ProductResponse(SQLModel):
    id: int
    name: str = Field(min_length=3, max_length=200)
    slug: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=3)
    price: int = Field(ge=0)  # 원 단위
    original_price: int | None = Field(default=None)  # 원래 가격 (할인 표시용)
    stock: int = Field(default=0, ge=0)
    is_active: bool | None = Field(default=True)
    is_featured: bool | None = Field(default=False)  # 추천 상품
    category_id: int
    category: CategoryResponse | None
    images: list[ProductImageResponse] | None

    model_config = {"from_attributes": True}


class ProductWithOneThumbImage(SQLModel):
    id: int
    name: str = Field(min_length=3, max_length=200)
    slug: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=3)
    price: int = Field(ge=0)  # 원 단위
    original_price: int | None = Field(default=None)  # 원래 가격 (할인 표시용)
    stock: int = Field(default=0, ge=0)
    is_active: bool | None = Field(default=True)
    is_featured: bool | None = Field(default=False)  # 추천 상품
    category_id: int
    thumb_url: str | None

    model_config = {"from_attributes": True}


class ProductUpdate(SQLModel):
    """상품 수정"""
    name: str | None = Field(default=None, min_length=3, max_length=200)
    slug: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, min_length=3)
    price: int | None = Field(default=None, ge=0)  # 원 단위
    original_price: int | None = Field(default=None)  # 원래 가격 (할인 표시용)
    stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = Field(default=True)
    is_featured: bool | None = Field(default=False)  # 추천 상품

    category_id: int | None = Field(default=None)
