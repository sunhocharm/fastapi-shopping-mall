from datetime import datetime, UTC
from sqlalchemy_utc import UtcDateTime
from pydantic import AwareDatetime

from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, func
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.model.order_model import Order


class PaymentMethod(str, Enum):
    """결제 수단"""
    CARD = "card"           # 카드
    TRANSFER = "transfer"   # 계좌이체
    VIRTUAL = "virtual"     # 가상계좌
    PHONE = "phone"         # 휴대폰


class PaymentStatus(str, Enum):
    """결제 상태"""
    PENDING = "pending"      # 대기
    COMPLETED = "completed"  # 완료
    FAILED = "failed"        # 실패
    CANCELLED = "cancelled"  # 취소


class Payment(SQLModel, table=True):
    """결제 테이블"""
    __tablename__ = "payments"

    id: int | None = Field(default=None, primary_key=True)
    # foreign keys
    order_id: int = Field(foreign_key="orders.id", unique=True)

    # 결제 정보
    method: PaymentMethod | None = Field(default=None)
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    amount: int  # 결제 금액

    # PG사 정보 (토스페이먼츠)
    payment_key: str | None = None  # PG사 결제 키
    receipt_url: str | None = None  # 영수증 URL


    completed_at: datetime | None = None
    created_at: AwareDatetime | None = Field(default=None, sa_type=UtcDateTime, sa_column_kwargs={"server_default": func.now()})

    # relationships
    order: "Order" = Relationship(back_populates="payment")
