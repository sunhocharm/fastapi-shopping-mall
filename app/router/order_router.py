from loguru import logger

from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import RedirectResponse

from app.dependencies import TemplatesDep
from app.dependencies import CurrentUser

from app.dependency.order_dep import OrderServiceDep
from app.dependency.payment_dep import PaymentServiceDep
from app.model.order_model import OrderStatus

from app.custom_exceptions import EntityNotFoundError


router = APIRouter() # prefix="/orders", tags=["orders"]


@router.get("")
async def order_list(
    request: Request,
    order_service: OrderServiceDep,
    current_user: CurrentUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ order_list ]]\n\n")
    """주문 내역 목록"""

    orders = await order_service.get_user_orders(current_user.id)

    return templates.TemplateResponse(
        request=request,
        name="orders/list.html",
        context={ "orders": orders, "page": 1 }
    )


@router.get("/{order_number}")
async def order_detail(
    request: Request,
    order_number: str,
    order_service: OrderServiceDep,
    current_user: CurrentUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ order_detail ]]\n\n")
    """주문 상세"""

    try:
        order = await order_service.get_order_by_number(order_number)
    except Exception as err:
        raise EntityNotFoundError(str(err))

    # try:
    #     validate_order_access(session, order, user)
    # except OrderAccessError:
    #     raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

    return templates.TemplateResponse(
        request=request, name="orders/detail.html", context={"order": order}
    )


@router.post("/{order_number}/cancel")
async def cancel_order(
    request: Request,
    order_number: str,
    order_service: OrderServiceDep,
    payment_service: PaymentServiceDep,
    current_user: CurrentUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ cancel_order ]]\n\n")
    """주문 취소"""

    try:
        order = await order_service.get_order_by_number(order_number)
    except Exception as err:
        raise EntityNotFoundError(str(err))

    try:
        order_service.validate_order_access(order, current_user)
        order_service.validate_order_cancellable(order)
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))

    # 결제 완료된 경우 PG사 취소
    do_cancel_payment = False
    if order.status == OrderStatus.PAID and order.payment.payment_key:
        result = await payment_service.cancel_payment(
            payment_key=order.payment.payment_key, cancel_reason="고객 요청에 의한 취소"
        )

        if not result["success"]:
            error = result["error"]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"결제 취소 실패: {error.get('message')}"
            )

        # 결제 상태 업데이트
        do_cancel_payment = True

    # 주문 취소
    await order_service.cancel_order(order=order, cancel_payment=do_cancel_payment)

    return RedirectResponse(url=f"/orders/{order_number}", status_code=303)
