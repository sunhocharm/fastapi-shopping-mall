from typing import Annotated

from fastapi import Depends, Cookie, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from sqlmodel.ext.asyncio.session import AsyncSession
from app.model.user_model import User, UserRole
from app.database import SessionDep

from app.repository.cart_repo import CartRepository
from app.service.cart_service import CartService

from app.util.auth_util import verify_access_token
from app.util.string_util import str_decode

import redis.asyncio as async_redis
from app.redis import get_redis

from app.custom_exceptions import CustomCredentialError, CustomPermissionError


BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=TEMPLATES_DIR)


# async def get_templates():
def get_templates():
    return templates


TemplatesDep = Annotated[Jinja2Templates, Depends(get_templates)]


async def get_redis_client() -> async_redis.Redis:
    return await get_redis()    


RedisDep = Annotated[async_redis.Redis, Depends(get_redis_client)]


async def _get_current_user(
    access_token: str, 
    session: AsyncSession, 
) -> User:
    payload = verify_access_token(access_token)
    if not payload:
        return None        

    str_user_id = str_decode(payload.get("sub"))
    try:
        int_user_id = int(str_user_id)
    except (TypeError, ValueError):
        return None        

    db_user = await session.get(User, int_user_id)
    if not db_user:
        return None

    return db_user
    

async def get_current_user_optional(
    *,
    request: Request, # Request 객체 주입 받기
    access_token: Annotated[str | None, Cookie()] = None,
    session: SessionDep
) -> User | None:
    # 1. 미들웨어 캐시 확인
    if getattr(request.state, "user", None) is not None:
        return request.state.user
    
    if not access_token:
        return None

    db_user = await _get_current_user(access_token, session)
    if not db_user:
        return None

    return db_user


async def get_current_user(
    *,
    request: Request, # Request 객체 주입 받기
    access_token: Annotated[str | None, Cookie()] = None,
    session: SessionDep
) -> User:
    # 1. 미들웨어 캐시 확인
    if getattr(request.state, "user", None) is not None:
        return request.state.user

    if not access_token:
        raise CustomCredentialError

    db_user = await _get_current_user(access_token, session)
    if not db_user:
        raise CustomCredentialError
    
    return db_user


async def get_current_admin_user(
    *,
    request: Request, # Request 객체 주입 받기
    access_token: Annotated[str | None, Cookie()] = None,
    session: SessionDep
) -> User:
    # 1. 미들웨어 캐시 확인
    admin_user = getattr(request.state, "user", None)
    
    # 캐시에 없다면 직접 조회
    if not admin_user:
        if not access_token:
            raise CustomCredentialError
        admin_user = await _get_current_user(access_token, session)
        if not admin_user:
            raise CustomCredentialError

    # 2. 권한 체크
    if admin_user.role != UserRole.ADMIN:
        raise CustomPermissionError

    return admin_user


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentAdminUser = Annotated[User, Depends(get_current_admin_user)]
CurrentUserOptional = Annotated[User | None, Depends(get_current_user_optional)]


# 로그인이 필요한 페이지에서 비로그인 시 로그인 페이지로 이동합니다.
async def require_login(request: Request, user: CurrentUserOptional) -> User | RedirectResponse:
    """로그인 필수 (리다이렉트)"""
    if not user:
        return RedirectResponse(
            url=f"/login?next={request.url.path}",
            status_code=303
        )
    return user


RequireLoginDep = Annotated[User | None, Depends(require_login)]




# async def get_cart_count(
#     cart=Depends(get_current_cart)
# ) -> int:
#     """장바구니 상품 수"""
#     if not cart:
#         return 0
#     return cart.total_quantity