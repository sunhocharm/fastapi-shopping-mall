from datetime import datetime
from sqlmodel import SQLModel

from app.model.payment_model import PaymentStatus, PaymentMethod


class PaymentCreate(SQLModel):
    order_id: int

    # 결제 정보
    method: PaymentMethod
    status: PaymentStatus
    amount: int  # 결제 금액

    # PG사 정보 (토스페이먼츠)
    payment_key: str
    receipt_url: str

    completed_at: datetime | None = None
