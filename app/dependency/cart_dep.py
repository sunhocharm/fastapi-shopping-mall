from typing import Annotated
from fastapi import Depends

from app.database import SessionDep

from ..repository.cart_repo import CartRepository
from ..service.cart_service import CartService


def get_cart_service(session: SessionDep) -> CartService:
    return CartService(CartRepository(session))


CartServiceDep = Annotated[CartService, Depends(get_cart_service)]
