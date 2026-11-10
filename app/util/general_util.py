from typing import Any
from fastapi import Request

from app.model.user_model import User
from .string_util import generate_urlsafe_token, hash_token

import re
from app.custom_exceptions import CustomBadRequestError


def validate_password(password: str) -> None:
    """
    비밀번호 정책 검증
    - 최소 8자
    - 영문, 숫자 포함
    """
    if len(password) < 8:
        raise CustomBadRequestError("비밀번호는 8자 이상이어야 합니다")

    if not re.search(r"[A-Za-z]", password):
        raise CustomBadRequestError("비밀번호에 영문자를 포함해야 합니다")

    if not re.search(r"\d", password):
        raise CustomBadRequestError("비밀번호에 숫자를 포함해야 합니다")



def get_cart_identifier(request: Request, user: User | None) -> dict[str, Any]:
    """장바구니 식별자 반환"""
    is_new_session = False
    session_id = request.cookies.get("cart_session")
    if not session_id:
        # session_id = uuid4().hex
        is_new_session = True
        session_id = generate_urlsafe_token()
    
    session_id_hashed = hash_token(session_id)

    user_id = request.state.user.id if request.state.user else None
    user_id = user.id if (not user_id) and user else None

    return (user_id, session_id, session_id_hashed, is_new_session)
