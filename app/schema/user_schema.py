from pydantic import EmailStr
from sqlmodel import SQLModel, Field


class UserCreate(SQLModel):
    """회원가입"""
    email: EmailStr = Field(max_length=255)
    password: str
    password_confirm: str
    name: str = Field(min_length=3, max_length=100)
    phone: str | None = Field(default=None, max_length=20)


class UserUpdate(SQLModel):
    """회원정보 수정"""
    name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)


class UserResponse(SQLModel):
    name: str
    phone: str


class UserLogin(SQLModel):
    """로그인"""
    email: str
    password: str
    next: str | None = Field(default=None)


class AddressCreate(SQLModel):
    """배송지 생성"""
    name: str = Field(max_length=50)  # 배송지명 (집, 회사 등)
    recipient: str = Field(max_length=100)  # 수령인
    phone: str = Field(max_length=20)
    zipcode: str = Field(max_length=10)
    address1: str = Field(max_length=200)  # 기본 주소
    address2: str | None = Field(default=None, max_length=200)  # 상세 주소
    is_default: bool | None = Field(default=False)


class AddressUpdate(SQLModel):
    """배송지 수정"""
    name: str | None = Field(default=None, max_length=50)  # 배송지명 (집, 회사 등)
    recipient: str | None = Field(default=None, max_length=100)  # 수령인
    phone: str | None = Field(default=None, max_length=20)
    zipcode: str | None = Field(default=None, max_length=10)
    address1: str | None = Field(default=None, max_length=200)  # 기본 주소
    address2: str | None = Field(default=None, max_length=200)  # 상세 주소
    is_default: bool | None = Field(default=False)
