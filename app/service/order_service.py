from loguru import logger
from typing import Any

import random
import string
from datetime import datetime

from app.repository.order_repo import OrderRepository

from app.model.user_model import User
from app.model.cart_model import Cart
from app.model.order_model import Order, OrderStatus

from app.custom_exceptions import EntityNotFoundError, CustomPermissionError


class OrderService:
    def __init__(self, repo: OrderRepository) -> None:
        self.repo = repo


    def validate_order_access(self, order: Order, user: User) -> None:
        """주문 접근 권한 검증"""
        if order.user_id != user.id:
            raise CustomPermissionError("접근 권한이 없습니다")


    def validate_order_cancellable(self, order: Order) -> None:
        """취소 가능 여부 검증"""

        non_cancellable = [
            OrderStatus.SHIPPING,
            OrderStatus.DELIVERED,
            OrderStatus.CANCELLED
        ]

        if order.status in non_cancellable:
            raise CustomPermissionError("취소할 수 없는 주문입니다")


    def generate_order_number(self) -> str:
        """
        주문번호 생성
        형식: YYYYMMDD-XXXXXX (예: 20240315-A3B2C1)
        """
        date_part = datetime.now().strftime("%Y%m%d")
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{date_part}-{random_part}"


    async def cancel_order(self, order: Order, cancel_payment: bool = False) -> None:
        await self.repo.cancel_order(order, cancel_payment=cancel_payment)


    async def create_new_order(
        self, 
        user_id: int, 
        order_dict: dict[str, Any], 
        cart: Cart, 
        shipping_fee: int, 
    ) -> Order:
        logger.info("\n\n\t시작: create_new_order in OrderService\n")

        order_dict["user_id"] = user_id
        order_dict["order_number"] = self.generate_order_number()
        order_dict["shipping_fee"] = shipping_fee
        order_dict["total_price"] = cart.total_price
        order_dict["final_price"] = cart.total_price - shipping_fee

        logger.info("\n\n\t끝: create_new_order in OrderService\n\n")
        return await self.repo.create_new_order(order_dict, cart.items)


    async def get_user_orders(self, user_id: int) -> list[Order]:
        return await self.repo.get_user_orders(user_id)


    async def get_order_by_number(self, order_number: str) -> Order:
        order = await self.repo.get_order_by_number(order_number)
        if not order:
            raise EntityNotFoundError
        return order


    async def get_order_by_id(self, order_id: int) -> Order:
        order = await self.repo.get_order_by_id(order_id)
        if not order:
            raise EntityNotFoundError
        return order


    async def get_order_status_counts(self) -> dict[str, int]:
        return await self.repo.get_order_status_counts()


    async def get_all_orders(self, status: str | None, skip: int | None = 0, limit: int | None = 10) -> list[Order]:
        return await self.repo.get_all_orders(status=status, skip=skip, limit=limit)

