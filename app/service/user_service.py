from typing import Any
from ..repository.user_repo import UserRepository
from ..model.user_model import User, UserRole, Address

from app.util.auth_util import verify_password, hash_password
from app.util.general_util import validate_password
from app.custom_exceptions import (
    EntityNotFoundError, CustomCredentialError, CustomPermissionError, CustomBadRequestError
)


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo


    async def create_user(self, user_dict: dict[str, Any]) -> User:
        if (not user_dict.get("password")) or (user_dict.get("password") != user_dict.get("password_confirm")):
            raise CustomBadRequestError("비밀번호 확인 / 비밀번호가 일치하지 않습니다")

        # 이메일 중복 확인
        existing_user = await self.repo.get_user_by_email(user_dict.get("email", None))
        if existing_user:
            raise CustomBadRequestError("이미 사용 중인 이메일입니다")

        # 비밀번호 정책 확인
        plain_pwd = user_dict.get("password", None)
        validate_password(plain_pwd)

        hashed_password = hash_password(plain_pwd)
        user_dict["hashed_password"] = hashed_password

        await self.repo.create_user(user_dict)


    async def login_user(self, user_email: str, user_pwd: str, for_admin: bool = False) -> User:
        db_user = await self.repo.get_user_by_email(user_email)
        if (not db_user) or (not verify_password(user_pwd, db_user.hashed_password)):
            raise CustomCredentialError("이메일 또는 비밀번호를 확인하세요")

        if for_admin and (db_user.role != UserRole.ADMIN):
            raise CustomPermissionError("관리자가 아닙니다.")            

        await self.repo.update_user_last_login_time(db_user)

        return db_user


    async def get_user_addresses(self, user_id: int) -> list[Address] | None:
        return await self.repo.get_user_addresses(user_id)
