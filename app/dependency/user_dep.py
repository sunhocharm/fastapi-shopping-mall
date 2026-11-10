from typing import Annotated
from fastapi import Depends

from app.database import SessionDep
from ..repository.user_repo import UserRepository
from ..service.user_service import UserService


async def get_user_service(session: SessionDep) -> UserService:
    return UserService(UserRepository(session))

UserServiceDep = Annotated[UserService, Depends(get_user_service)]
