from typing import Annotated
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from loguru import logger

from app.dependencies import TemplatesDep, CurrentUserOptional
from app.schema.user_schema import UserCreate, UserLogin
from app.dependency.user_dep import UserServiceDep
from app.dependency.cart_dep import CartServiceDep

from app.util.auth_util import create_access_token, create_refresh_token
from app.util.cookie_util import set_access_and_refresh_token_in_cookie, delete_access_and_refresh_token_in_cookie
from app.util.general_util import get_cart_identifier

router = APIRouter()   # [prefix="", tags=["auth"]


@router.get("/register")
async def register_form(request: Request, templates: TemplatesDep, user: CurrentUserOptional):
    logger.info("\n\n\t[[ register_form ]]\n\n")

    if user:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={"errors": {}}
    )


@router.post("/register")
async def register(
    request: Request,
    req_data: Annotated[UserCreate, Form()],
    user_service: UserServiceDep, 
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ register ]]\n\n")

    user_dict = req_data.model_dump()
    try:
        await user_service.create_user(user_dict)
    except Exception as err:
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={ "server_data": user_dict, "server_errors": str(err) }
        )

    # 성공 시 로그인 페이지로
    return RedirectResponse(url="/login?message=registered", status_code=303)


@router.get("/login")
async def login_form(
    *,
    request: Request,
    message: str | None = None,
    next: str | None = None,
    templates: TemplatesDep,
    user: CurrentUserOptional
):
    logger.info("\n\n\t[[ login_form ]]\n\n")

    if user:
        return RedirectResponse(url="/", status_code=303)

    messages = {
        "registered": "회원가입이 완료되었습니다. 로그인해주세요.",
        "logout": "로그아웃되었습니다."
    }

    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "message": messages.get(message),
            "next": next,
        }
    )


@router.post("/login")
async def login(
    request: Request,
    req_data: Annotated[UserLogin, Form()],
    user_service: UserServiceDep,
    cart_service: CartServiceDep,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ login ]]\n\n")
    next = req_data.next if req_data.next else "/"

    try:
        db_user = await user_service.login_user(req_data.email, req_data.password, for_admin=False)
    except Exception as err:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "server_errors": str(err),
                "email": req_data.email,
                "next": next
            }
        )

    # -----------------------------------------------------------------------------------------#
    # non login 상태의 cart ==> login 상태의 cart 로 변환
    # 로그인 직후에 호출된다. from auth_router: login
    (user_id_in_session, session_id, session_id_hashed, is_new_session) = get_cart_identifier(request, db_user)
    if not is_new_session:
        await cart_service.process_non_login_cart(user_id_in_session, session_id_hashed)


    access_token = create_access_token(str(db_user.id))
    refresh_token = create_refresh_token(str(db_user.id))

    response = RedirectResponse(url=next, status_code=303)
    set_access_and_refresh_token_in_cookie(response, access_token, refresh_token)
    return response


@router.post("/logout")
async def logout(request: Request):
    logger.info("\n\n\t[[ logout ]]\n\n")

    response = RedirectResponse(url="/login?message=logout", status_code=303)
    delete_access_and_refresh_token_in_cookie(response)
    return response
