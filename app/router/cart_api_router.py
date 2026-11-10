from loguru import logger
from typing import Any
# from uuid import uuid4
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse


from app.dependencies import RedisDep
from app.dependencies import CurrentUserOptional

from app.model.user_model import User
from app.dependency.product_dep import ProductServiceDep
from app.dependency.cart_dep import CartServiceDep
from app.schema.cart_schema import AddToCartRequest, UpdateCartItemRequest

from app.util.cookie_util import set_cart_session_token_in_cookie
from app.util.general_util import get_cart_identifier

from app.custom_exceptions import EntityNotFoundError, CustomBadRequestError

# import redis.asyncio as async_redis


router = APIRouter()    # prefix="/api/cart", tags=["cart-api"])
# protocol=2 옵션을 추가하여 구형 레디스 서버(5.x)와의 호환성을 맞춰줍니다.
# redis_client = async_redis.from_url("redis://127.0.0.1:6379", decode_responses=True, protocol=2)


@router.post("/add")
async def api_add_to_cart(
    request: Request,
    req_data: AddToCartRequest,
    product_service: ProductServiceDep,
    cart_service: CartServiceDep,
    user: CurrentUserOptional,
    redis_client: RedisDep
):
    """장바구니 담기"""
    logger.info("\n\n\t[[ api_add_to_cart ]]\n\n")

    # 상품 확인
    try:
        db_product = await product_service.get_product_only_by_id(req_data.product_id)
    except Exception as err:
        logger.error(err)
        raise EntityNotFoundError("상품을 찾을 수 없습니다")

    if not db_product.is_active:
        logger.error("product is not active")
        raise EntityNotFoundError("상품을 찾을 수 없습니다")

    # 재고 확인
    if db_product.stock < req_data.quantity:
        logger.error("재고가 부족합니다")
        raise CustomBadRequestError("재고가 부족합니다")

    # 장바구니 가져오기
    (user_id_in_session, session_id, session_id_hashed, is_new_session) = get_cart_identifier(request, user)

    # 상품 추가
    cart_req_dict = req_data.model_dump()
    try:
        cart = await cart_service.get_or_update_or_create_cart(user_id_in_session, session_id_hashed, cart_req_dict)
    except Exception as err:
        logger.error(err)
        return JSONResponse({
            "success": False, "message": str(err), "cart_quantity": None
        })

    new_cached_total = cart.total_quantity
    redis_key = f"cart:total:{session_id_hashed}"
    exists = await redis_client.exists(redis_key)
    if exists:
        ttl = await redis_client.ttl(redis_key)
        await redis_client.set(redis_key, new_cached_total, ex=ttl)
    else:
        await redis_client.set(redis_key, new_cached_total, ex=1 * 24 * 60 * 60)

    # request.state.cart_total = new_cached_total
    # AL8TVB10iELgxDt4FIEpFsaNojOOvnIZ8s4hd-6whGw

    # 응답
    response = JSONResponse({
        "success": True,
        "message": "장바구니에 담았습니다",
        "cart_total": new_cached_total # cart.total_quantity
    })

    src_session_id = request.cookies.get("cart_session")
    if not src_session_id:
        # 비회원 / login user 모두에 대해 cookie에 넣는다.
        set_cart_session_token_in_cookie(response, session_id)

    return response


# @router.put("/items/{item_id}")
# async def update_cart_item(
#     item_id: int,
#     data: UpdateCartItemRequest,
#     session: Session = Depends(get_session)
# ):
#     """수량 변경"""
#     item = cart_crud.update_cart_item(session, item_id, data.quantity)

#     if data.quantity <= 0:
#         return {"success": True, "message": "상품이 삭제되었습니다"}

#     if not item:
#         raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

#     return {
#         "success": True,
#         "quantity": item.quantity,
#         "subtotal": item.subtotal
#     }

# @router.delete("/items/{item_id}")
# async def remove_cart_item(
#     item_id: int,
#     session: Session = Depends(get_session)
# ):
#     """상품 삭제"""
#     success = cart_crud.remove_from_cart(session, item_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

#     return {"success": True, "message": "삭제되었습니다"}
