from loguru import logger

from typing import Annotated
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from app.dependencies import TemplatesDep
from app.dependencies import CurrentUserOptional

from app.dependency.user_dep import UserServiceDep
from app.model.user_model import UserRole
from app.schema.user_schema import UserLogin

from app.util.auth_util import create_access_token, create_refresh_token
from app.util.cookie_util import set_access_and_refresh_token_in_cookie
# from app.custom_exceptions import EntityNotFoundError, CustomCredentialError, CustomPermissionError


router = APIRouter() # prefix="/admin", tags=["admin-auth"]


@router.get("/login")
async def admin_login_page(
    *,
    request: Request,
    templates: TemplatesDep,
    current_user: CurrentUserOptional
):
    logger.info("\n\n\t[[ admin_login_page ]]\n\n")

    if current_user and current_user.role == UserRole.ADMIN:
        return RedirectResponse(url="/admin", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={"errors": {}}
    )


@router.post("/login")
async def admin_login(
    request: Request,
    req_data: Annotated[UserLogin, Form()],
    templates: TemplatesDep, 
    user_service: UserServiceDep, 
):
    logger.info("\n\n\t[[ admin_login ]]\n\n")

    try:
        db_user = await user_service.login_user(req_data.email, req_data.password, for_admin=True)
    except Exception as err:
        return templates.TemplateResponse(
            request=request,
            name="admin/login.html",
            context={ "email": req_data.email, "errors": {"general": str(err)} }
        )

    access_token = create_access_token(str(db_user.id))
    refresh_token = create_refresh_token(str(db_user.id))
    
    response = RedirectResponse(url="/admin", status_code=303)
    set_access_and_refresh_token_in_cookie(response, access_token, refresh_token)
    return response
