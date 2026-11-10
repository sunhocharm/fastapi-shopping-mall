from app.config import settings
from typing import Annotated

from datetime import datetime
from loguru import logger

from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import RedirectResponse

from app.dependency.order_dep import OrderServiceDep
from app.dependency.payment_dep import PaymentServiceDep

from app.dependencies import TemplatesDep
from app.dependencies import CurrentUser

from app.model.order_model import OrderStatus
from app.model.payment_model import PaymentStatus
from app.schema.payment_schema import PaymentCreate


from app.custom_exceptions import EntityNotFoundError

router = APIRouter() # prefix="/payment", tags=["payment"]


@router.get("/success")     # for /payment/success
async def payment_success(
    request: Request,
    paymentType: Annotated[str, Query()],   # NORMAL
    orderId:  Annotated[str, Query()],
    paymentKey:  Annotated[str, Query()],
    amount:  Annotated[int, Query()],
    order_service: OrderServiceDep,
    payment_service: PaymentServiceDep,
    current_user: CurrentUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ payment_success ]]\n\n")
    """결제 성공 (리다이렉트)"""
    # 주문 조회
    try:
        order = await order_service.get_order_by_number(orderId)
    except Exception as err:
        raise EntityNotFoundError(str(err))

    # 권한 확인
    if order.user_id != current_user.id:
        return templates.TemplateResponse(
            request=request, name="payment/fail.html", context={"message": "접근 권한이 없습니다"}
        )

    # 금액 확인
    if order.final_price != amount:
        return templates.TemplateResponse(
            request=request, name="payment/fail.html", context={"message": "결제 금액이 일치하지 않습니다"}
        )

    # 결제 승인
    result = await payment_service.confirm_payment(paymentKey, orderId, amount)

    if not result["success"]:
        error = result["error"]
        return templates.TemplateResponse(
            request=request, 
            name="payment/fail.html", 
            context={"message": "결제 승인에 실패했습니다", "code": error.get("code")}
        )

    # 결제 정보 업데이트

    payment_data = result["data"]
      
    payment = PaymentCreate (
        order_id=order.id,
        method="transfer", # payment_data.get("method"), -------------- 임시로
        status=PaymentStatus.COMPLETED,
        amount=amount, 
        payment_key=paymentKey,
        receipt_url=payment_data.get("receipt", {}).get("url"),
        completed_at=datetime.now()
    )

    try:
        await payment_service.process_payment_ok(order.id, payment)
    except Exception as err:
        cancelled_ok = True
        cancel_result = await payment_service.cancel_payment(paymentKey, "내부처리에 실패하였습니다.")
        if cancel_result["success"]:
            logger.info("결재 취소 처리 OK")
        else:
            cancelled_ok = False
            error = cancel_result["error"]
            logger.error(f"결재 취소 처리 Fail: [{error}]")

        cancel_result_msg = "OK" if cancelled_ok else "Fail"
        return templates.TemplateResponse(
            request=request, 
            name="payment/fail.html", 
            context={ "code": 999, "order_id": orderId, "message": f"결제가 실패했습니다: [결제 취소 {cancel_result_msg}]"}
        )

    return templates.TemplateResponse(
        request=request, name="payment/success.html", context={"order": order}
    )


@router.get("/fail")    # for /payment/fail
async def payment_fail(
    *,
    request: Request,
    code: str | None = None,
    message: str | None  = None,
    orderId: str | None  = None,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ payment_fail ]]\n\n")
    """결제 실패 (리다이렉트)"""
    return templates.TemplateResponse(
        request=request,
        name="payment/fail.html",
        context={ "code": code, "order_id": orderId, "message": message or "결제가 실패했습니다"}
    )


@router.get("/{order_number}")
async def payment_page(
    request: Request,
    order_number: str,
    order_service: OrderServiceDep,
    current_user: CurrentUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ payment_page ]]\n\n")
    """결제 페이지"""
    try:
        order = await order_service.get_order_by_number(order_number)
    except Exception as err:
        raise EntityNotFoundError(str(err))

    # try:
    #     validate_order_access(session, order, user)
    # except OrderAccessError:
    #     raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

    # 이미 결제된 주문
    if order.status != OrderStatus.PENDING:
        return RedirectResponse(url=f"/orders/{order_number}", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="payment/checkout.html",
        context={
            "order": order,
            "client_key": settings.toss_client_key.get_secret_value(),
            "success_url": f"{settings.frontend_url}/payment/success",
            "fail_url": f"{settings.frontend_url}/payment/fail"
        }
    )
