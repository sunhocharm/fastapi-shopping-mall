from datetime import datetime, UTC
from pydantic import AwareDatetime
from sqlalchemy_utc import UtcDateTime
from sqlmodel import SQLModel, Field, Relationship, func
from enum import Enum

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.model.order_model import Order


class UserRole(str, Enum):
    """회원 역할"""
    USER = "user"
    ADMIN = "admin"


class User(SQLModel, table=True):
    """회원 테이블"""
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    name: str
    phone: str | None = Field(default=None)
    role: UserRole | None = Field(default=UserRole.USER)
    is_active: bool | None = Field(default=True)
    hashed_password: str

    last_login_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime)
    created_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now()})
    updated_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now(), "onupdate": lambda: datetime.now(tz=UTC)})

    # relationships
    orders: list["Order"] = Relationship(back_populates="user")
    addresses: list["Address"] = Relationship(back_populates="user")


class Address(SQLModel, table=True):
    """배송지 테이블"""
    __tablename__ = "addresses"

    id: int | None = Field(default=None, primary_key=True)
    name: str  # 배송지명 (집, 회사 등)
    recipient: str  # 수령인
    phone: str
    zipcode: str
    address1: str  # 기본 주소
    address2: str | None = Field(default=None)  # 상세 주소
    is_default: bool | None = Field(default=False)

    # foreign keys
    user_id: int = Field(foreign_key="users.id")

    created_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now()})
    updated_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now(), "onupdate": lambda: datetime.now(tz=UTC)})

    # relationships
    user: User = Relationship(back_populates="addresses")
