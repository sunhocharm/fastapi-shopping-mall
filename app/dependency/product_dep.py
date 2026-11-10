from typing import Annotated
from fastapi import Depends

from app.database import SessionDep

from app.repository.product_repo import ProductRepository
from app.service.product_service import ProductService


async def get_product_service(session: SessionDep) -> ProductService:
    return ProductService(ProductRepository(session))


ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
