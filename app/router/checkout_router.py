from loguru import logger

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse

from app.dependencies import TemplatesDep
from app.dependencies import CurrentUser

from app.dependency.user_dep import UserServiceDep
from app.dependency.cart_dep import CartServiceDep
from app.dependency.order_dep import OrderServiceDep
from app.service.shipping_service import calculate_shipping_fee

from app.schema.order_schema import OrderCreate

from app.util.general_util import get_cart_identifier
from app.util.cookie_util import delete_cart_session_token_in_cookie

from app.service.cart_validation_error import CartValidationError
import redis.asyncio as async_redis

router = APIRouter() # prefix="/checkout", tags=["checkout"]

redis_client = async_redis.from_url("redis://127.0.0.1:6379", decode_responses=True, protocol=2)


@router.get("")
async def checkout_page(
    request: Request,
    user_service: UserServiceDep,
    cart_service: CartServiceDep,
    current_user: CurrentUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ checkout_page ]]\n\n")
    """주문서 작성 페이지"""

    # 장바구니 확인
    (user_id_in_session, session_id, session_id_hashed, is_new_session) = get_cart_identifier(request, current_user)
    cart = await cart_service.get_current_cart(user_id=current_user.id, cart_session_id=session_id_hashed)


    if (not cart) or (not cart.items):
        return RedirectResponse(url="/cart", status_code=303)

    # 장바구니 검증
    try:
        await cart_service.validate_cart_items(cart)
    except CartValidationError as err:
        return templates.TemplateResponse(
            request=request, name="checkout/error.html", context={"errors": err.errors}
        )
    except Exception as err:
        return templates.TemplateResponse(
            request=request, name="checkout/error.html", context={"errors": [str(err)]}
        )

    # 배송지 목록
    addresses = await user_service.get_user_addresses(current_user.id)
    default_address = next((a for a in addresses if a.is_default), None)

    # 배송비 계산
    shipping_fee = calculate_shipping_fee(cart.total_price)
    final_price = cart.total_price + shipping_fee

    return templates.TemplateResponse(
        request=request,
        name="checkout/index.html",
        context={
            "cart": cart,
            "addresses": addresses,
            "default_address": default_address,
            "shipping_fee": shipping_fee,
            "final_price": final_price
        }
    )


@router.post("")
async def create_order(
    request: Request,
    req_data: Annotated[OrderCreate, Form()],
    cart_service: CartServiceDep,
    order_service: OrderServiceDep,
    current_user: CurrentUser,
    templates: TemplatesDep
):
    """주문 생성"""
    logger.info("\n\n\t[[ create_order ]]\n\n")

    (user_id_in_session, session_id, session_id_hashed, is_new_session) = get_cart_identifier(request, current_user)
    cart = await cart_service.get_current_cart(user_id=current_user.id, cart_session_id=session_id_hashed)

    # 장바구니 확인
    if (not cart) or (not cart.items):
        return RedirectResponse(url="/cart", status_code=303)

    # 장바구니 검증
    try:
        await cart_service.validate_cart_items(cart)
    except CartValidationError as err:
        return templates.TemplateResponse(
            request=request, name="checkout/error.html", context={"errors": err.errors}
        )
    except Exception as err:
        return templates.TemplateResponse(
            request=request, name="checkout/error.html", context={"errors": [str(err)]}
        )


    # 배송비 계산
    shipping_fee = calculate_shipping_fee(cart.total_price)

    # 주문 생성
    order_dict = req_data.model_dump()
    order_dict["shipping_fee"] = shipping_fee
    try:
        order = await order_service.create_new_order(
            current_user.id, 
            order_dict, 
            cart, 
            shipping_fee, 
        )
    except Exception as err:
        return templates.TemplateResponse(
            request=request, name="checkout/error.html", context={"errors": [str(err)]}
        )

    response = RedirectResponse(
        url=f"/payment/{order.order_number}", status_code=303
    )
    # # 장바구니 비우기
    await cart_service.clear_cart(current_user.id)
    delete_cart_session_token_in_cookie(response)
    request.state.cart_total = None

    redis_key = f"cart:total:{session_id_hashed}"
    exists = await redis_client.exists(redis_key)
    if exists:
        await redis_client.unlink(redis_key)


    # 결제 페이지로 이동
    return response
