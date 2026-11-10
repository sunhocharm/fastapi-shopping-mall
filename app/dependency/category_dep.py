from typing import Annotated
from fastapi import Depends

from app.database import SessionDep

from ..repository.category_repo import CategoryRepository
from ..service.category_service import CategoryService


async def get_category_service(session: SessionDep) -> CategoryService:
    return CategoryService(CategoryRepository(session))


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
