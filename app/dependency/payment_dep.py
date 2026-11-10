from typing import Annotated
from fastapi import Depends

from app.database import SessionDep

from app.repository.payment_repo import PaymentRepository
from app.service.payment_service import PaymentService


def get_payment_service(session: SessionDep) -> PaymentService:
    return PaymentService(PaymentRepository(session))


PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
