from typing import Annotated
from fastapi import Depends

from app.database import SessionDep
from app.repository.order_repo import OrderRepository
from app.service.order_service import OrderService


async def _get_order_service(session: SessionDep) -> OrderService:
    return OrderService(OrderRepository(session))


OrderServiceDep = Annotated[OrderService, Depends(_get_order_service)]
