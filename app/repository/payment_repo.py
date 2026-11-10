from loguru import logger
from typing import Any
from datetime import datetime
from sqlalchemy.exc import DatabaseError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model.payment_model import Payment, PaymentStatus, PaymentMethod
from app.model.order_model import Order, OrderStatus

from app.custom_exceptions import CustomDatabaseError, BaseBusinessError


class PaymentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    async def _create_payment(self, payment_dict: dict[str, Any]) -> None:
        logger.info("\n\tstart: _create_payment")
        db_payment = Payment.model_validate(payment_dict)
        self.session.add(db_payment)
        self.session.flush()
        logger.info("\n\tstart: _create_payment")


    # 주문 상태 업데이트
    async def update_order_status(self, order_id: int, status: OrderStatus) -> None:
        logger.info("\n\tstart: update_order_status")

        prev_order = await self.session.get(Order, order_id)
        prev_order.status = status

        # 상태별 시간 기록
        now = datetime.now()
        if status == OrderStatus.PAID:
            prev_order.paid_at = now
        elif status == OrderStatus.SHIPPING:
            prev_order.shipped_at = now
        elif status == OrderStatus.DELIVERED:
            prev_order.delivered_at = now
        elif status == OrderStatus.CANCELLED:
            prev_order.cancelled_at = now

        self.session.add(prev_order)
        await self.session.flush()

        logger.info("\n\tstart: update_order_status")


    async def process_payment_ok(self, order_id: int, payment_dict: dict[str, Any]) -> None:
        logger.info("\n\n\t시작: process_payment_ok in PaymentRepository\n")

        try:
            await self._create_payment(payment_dict)
            await self.update_order_status(order_id, status=OrderStatus.PAID)

            await self.session.commit()

        except (DatabaseError, Exception) as err:
            await self.session.rollback()
            logger.err(err)
            if isinstance(err, DatabaseError):
                raise CustomDatabaseError
            raise BaseBusinessError

        logger.info("\n\n\t끝: process_payment_ok in PaymentRepository\n\n")
    