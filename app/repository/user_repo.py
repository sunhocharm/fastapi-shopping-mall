from typing import Any
from datetime import datetime, UTC
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from ..model.user_model import User, Address
from app.custom_exceptions import DatabaseConstraintError, EntityAlreadyExistsError


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    async def create_user(self, user_dict: dict[str, Any]) -> None:
        db_user = User.model_validate(user_dict)
        self.session.add(db_user)
        try:
            await self.session.commit()
        except IntegrityError as err:
            await self.session.rollback()

            # if "unique constraint" in str(err.orig).lower():
            #     raise EntityAlreadyExistsError("DB에 Calendar가 이미 있습니다.") from err

            raise DatabaseConstraintError("데이터베이스 제약 조건 위반이 발생했습니다.") from err

    async def update_user_last_login_time(self, db_user: User) -> None:
        # now = datetime.now(tz=UTC)
        db_user.last_login_at = datetime.now(tz=UTC)
        self.session.add(db_user)
        await self.session.commit()


    async def get_user_by_email(self, user_email: str) -> User:
        result = await self.session.exec(
            select(User).where(User.email == user_email)
        )
        return result.first()


    async def get_user_addresses(self, user_id: int) -> list[Address] | None:
        result = await self.session.exec(
            select(Address).where(Address.user_id == user_id)
        )
        return result.all()
