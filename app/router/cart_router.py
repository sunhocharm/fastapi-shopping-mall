from loguru import logger
from typing import Any, Annotated
# from uuid import uuid4
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse


from app.dependencies import CurrentUserOptional
from app.model.user_model import User
from app.dependency.product_dep import ProductServiceDep
from app.dependency.cart_dep import CartServiceDep
from app.dependencies import TemplatesDep, CurrentUserOptional, CurrentUser

from app.schema.cart_schema import AddToCartRequest, UpdateCartItemRequest

from app.util.cookie_util import set_cart_session_token_in_cookie
from app.util.general_util import get_cart_identifier

from app.custom_exceptions import EntityNotFoundError, CustomBadRequestError


router = APIRouter()    # prefix="/cart", tags=["cart-page"])


@router.get("")
async def cart_page(
    request: Request,
    cart_service: CartServiceDep,
    current_user: CurrentUser,
    templates: TemplatesDep
):
    """장바구니 페이지"""
    logger.info("\n\n\t[[ cart_page ]]\n\n")

    (user_id_in_session, session_id, session_id_hashed, is_new_session) = get_cart_identifier(request, current_user)
    cart = await cart_service.get_current_cart(user_id=current_user.id, cart_session_id=session_id_hashed)

    return templates.TemplateResponse(
        request=request,
        name="cart/index.html",
        context={ "cart": cart }
    )


@router.post("/update/{cartitem_id}")
async def update_item_qty(
    request: Request,
    cartitem_id: int,
    quantity: Annotated[int, Form()],
    cart_service: CartServiceDep,
    current_user: CurrentUser,
):
    logger.info("\n\n\t[[ update_item_qty ]]\n\n")

    await cart_service.update_cart_item_qty(cartitem_id, quantity)

    return RedirectResponse(url="/cart", status_code=303)