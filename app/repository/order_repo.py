from loguru import logger
from typing import Any
from datetime import datetime

from pydantic import ValidationError
from sqlalchemy import update, bindparam
from sqlalchemy.orm import selectinload, joinedload
from sqlmodel import select, func, case

from sqlalchemy.exc import DatabaseError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model.order_model import Order, OrderItem, OrderStatus
from app.model.cart_model import CartItem
from app.model.payment_model import Payment, PaymentStatus
from app.model.product_model import Product
from app.model.user_model import Address

from app.custom_exceptions import CustomDatabaseError, BaseBusinessError


class OrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    async def get_order_by_id(self, order_id: int) -> Order | None:
        result = await self.session.exec(
            select(Order)
            .options(
                # joinedload(Order.payment, innerjoin=False),
                selectinload(Order.items)
            )
            .where(Order.id == order_id)
        )
        return result.first()


    async def get_order_by_number(self, order_number: str) -> Order | None:
        result = await self.session.exec(
            select(Order)
            .options(
                joinedload(Order.payment, innerjoin=False),
                selectinload(Order.items)
            )
            .where(Order.order_number == order_number)
        )
        return result.first()


    async def get_user_orders(self, user_id: int) -> list[Order]:
        result = await self.session.exec(
            select(Order)
            .options(
                selectinload(Order.items)
            )
            .where(Order.user_id == user_id)
        )
        return result.all()


    async def _create_order(self, order_dict: dict[str, Any]) -> Order:
        logger.info("\n\tstart: _create_order")

        new_order = Order(
            order_number=order_dict.get("order_number", None),
            user_id=order_dict.get("user_id", None),
            status=order_dict.get("status", None),
            total_price=order_dict.get("total_price", None),
            shipping_fee=order_dict.get("shipping_fee", None),
            final_price=order_dict.get("final_price", None),
            recipient=order_dict.get("recipient", None),
            phone=order_dict.get("phone", None),
            zipcode=order_dict.get("zipcode", None),
            address1=order_dict.get("address1", None),
            address2=order_dict.get("address2", None),
            memo=order_dict.get("memo", None),
        )

        self.session.add(new_order)
        await self.session.flush()
        logger.info("\n\tend: _create_order")
        return new_order


    async def _create_order_items(self, order_id: int, cart_items: list[CartItem]) -> None:
        logger.info("\n\tstart: _create_order_items")
        for item in cart_items:
            new_item = OrderItem(
                order_id=order_id,
                product_id=item.product_id,
                product_name=item.product.name,
                product_price=item.product.price,
                quantity=item.quantity,
                subtotal=item.product.price * item.quantity
            )

            self.session.add(new_item)
        await self.session.flush()
        logger.info("\n\tend: _create_order_items")


    # async def _process_item_stock_for_order(self, cart_items: list[CartItem]) -> None:
    #     logger.info("\n\tstart: _process_item_stock_for_order")
    #     for item in cart_items:
    #         prev_product: Product = await self.session.get(prev_product, item.product_id)
    #         prev_product.stock -= item.quantity
    #         self.session.add(prev_product)
    #     logger.info("\n\tend: _process_item_stock_for_order")


    # upgrade version
    async def _process_item_stock_for_order(self, items_to_process: list[Product], is_cancel: bool = False) -> None:
        logger.info("\n\tstart: _process_item_stock_for_order")

        # ------------------------------------------------------------------------------------------ #
        # 1. 벌크 업데이트 파라미터 준비
        update_data = [
            { "b_id": item.product_id, "b_qty": item.quantity } for item in items_to_process
        ]

        # 2. Core Table 객체 사용
        product_table = Product.__table__

        # 3. 벌크 UPDATE 쿼리 작성
        stmt = (
            update(product_table)
            .where(product_table.c.id == bindparam("b_id"))
            # .values(
            #     stock=product_table.c.stock - bindparam("b_qty")
            # )
        )
        if is_cancel:
            stmt = stmt.values(stock=product_table.c.stock + bindparam("b_qty"))
        else:
            stmt = stmt.values(stock=product_table.c.stock - bindparam("b_qty"))


        # 4. 벌크 업데이트 실행
        await self.session.exec(stmt, params=update_data)
        await self.session.flush()
        # ------------------------------------------------------------------------------------------ #
        logger.info("\n\tend: _process_item_stock_for_order")


    async def _save_new_address(self, order_dict: dict[str, Any]) -> None:
        logger.info("\n\tstart: _save_new_address")
        do_save_address = order_dict.get("save_address", None)
        if not do_save_address:
            return None

        new_address = Address(
            name="새 배송지",
            recipient=order_dict["recipient"],
            phone=order_dict["phone"],
            zipcode=order_dict["zipcode"],
            address1=order_dict["address1"],
            address2=order_dict["address2"],
            is_default=False, 
            user_id=order_dict["user_id"]
        )
        self.session.add(new_address)
        await self.session.flush()
        logger.info("\n\tend: _save_new_address")


    async def create_new_order(
        self, 
        order_dict: dict[str, Any], 
        cart_items: list[CartItem], 
    ) -> Order:
        logger.info("\n\n\t시작: create_new_order in OrderRepository\n")

        order_dict["status"] = OrderStatus.PENDING

        try:
            new_order = await self._create_order(order_dict)
            await self._create_order_items(new_order.id, cart_items)
            await self._process_item_stock_for_order(items_to_process=cart_items, is_cancel=False)
            await self._save_new_address(order_dict)

            await self.session.commit()

        except (DatabaseError, Exception) as err:
            await self.session.rollback()
            logger.error(err)
            if isinstance(err, DatabaseError):
                raise CustomDatabaseError
            raise BaseBusinessError

        logger.info("\n\n\t끝: create_new_order in OrderRepository\n\n")
        return new_order


    async def cancel_order(self, order: Order, cancel_payment: bool = False) -> None:
        logger.info("\n\n\t시작: cancel_order in OrderRepository\n")

        order_id = order.id

        try:
            if cancel_payment:
                payment = await self.session.exec(select(Payment).where(Payment.order_id == order_id))
                db_payment = payment.first()
                db_payment.status = PaymentStatus.CANCELLED
                self.session.add(db_payment)

            # Product stock 를 되돌린다.
            await self._process_item_stock_for_order(items_to_process=order.items, is_cancel=True)

            db_order = await self.session.get(Order, order_id)
            db_order.status = OrderStatus.CANCELLED
            db_order.cancelled_at = datetime.now()
            self.session.add(db_order)

            await self.session.commit()

        except (DatabaseError, Exception) as err:
            await self.session.rollback()
            logger.error(err)
            if isinstance(err, DatabaseError):
                raise CustomDatabaseError
            raise BaseBusinessError

        logger.info("\n\n\t끝: cancel_order in OrderRepository\n")


    async def get_order_status_counts(self) -> dict[str, int]:
        # 1. 쿼리 빌드: 단일 행(1 row) 결과만 반환하도록 조건부 집계 구성
        statement = select(
            func.count(Order.id).label("all_count"),
            func.count(case((Order.status == OrderStatus.PENDING, 1))).label("pending"),
            func.count(case((Order.status == OrderStatus.PAID, 1))).label("paid"),
            func.count(case((Order.status == OrderStatus.PREPARING, 1))).label("preparing"),
            func.count(case((Order.status == OrderStatus.SHIPPING, 1))).label("shipping"),
            func.count(case((Order.status == OrderStatus.DELIVERED, 1))).label("delivered"),
            func.count(case((Order.status == OrderStatus.CANCELLED, 1))).label("cancelled"),
        )
        
        # 2. 비동기 쿼리 실행
        result = await self.session.exec(statement)
        
        # 3. 결과 행 꺼내기 (단일 행 결과이므로 .first() 또는 .one() 사용)
        counts = result.first()
        
        if not counts:
            return {"all": 0, "pending": 0, "paid": 0, "preparing": 0, "shipping": 0, "delivered": 0, "cancelled": 0}
            
        # 4. 딕셔너리로 깔끔하게 패킹하여 반환
        return {
            "all": counts.all_count,
            "pending": counts.pending,
            "paid": counts.paid,
            "preparing": counts.preparing,
            "shipping": counts.shipping,
            "delivered": counts.delivered,
            "cancelled": counts.cancelled,
        }

    async def get_all_orders(self, status: str | None, skip: int | None = 0, limit: int | None = 10) -> list[Order]:
        result = await self.session.exec(
            select(Order)
            .options(
                selectinload(Order.items)
            )
        )
        return result.all()
