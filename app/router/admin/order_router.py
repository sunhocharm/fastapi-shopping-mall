from loguru import logger
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Form, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.dependencies import TemplatesDep
from app.dependencies import CurrentAdminUser

from app.dependency.user_dep import UserServiceDep
from app.dependency.order_dep import OrderServiceDep
from app.model.user_model import UserRole
from app.schema.user_schema import UserLogin


router = APIRouter() # prefix="/admin/orders", tags=["admin-orders"]

@router.get("")
async def admin_order_list(
    *,
    request: Request,
    status: Annotated[str | None, Query()] = None,
    page: int = Query(1, ge=1),
    order_service: OrderServiceDep,
    admin_user: CurrentAdminUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ admin_order_list ]]\n\n")

    """주문 목록"""
    per_page = 20
    skip = (page - 1) * per_page

    # # 상태 필터
    # order_status = None
    # if status:
    #     try:
    #         order_status = OrderStatus(status)
    #     except ValueError:
    #         pass

    orders = await order_service.get_all_orders(status, skip=skip, limit=per_page)
    count_by_status = await order_service.get_order_status_counts()

    return templates.TemplateResponse(
        request=request,
        name="admin/orders/list.html",
        context={
            "orders": orders,
            "status": status,
            "status_counts": count_by_status,
            "page": page,
            "total": count_by_status["all"],
            "per_page": per_page
        }
    )

@router.get("/{order_id}")
async def admin_order_detail(
    request: Request,
    order_id: int,
    order_service: OrderServiceDep,
    admin_user: CurrentAdminUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ admin_order_detail ]]\n\n")
    """주문 상세"""
    order = await order_service.get_order_by_id(order_id)

    return templates.TemplateResponse(
        request=request,
        name="admin/orders/detail.html",
        context={ "order": order }
    )

# @router.post("/{order_id}/status")
# async def update_order_status(
#     order_id: int,
#     status: str = Form(...),
#     session: Session = Depends(get_session),
#     admin = Depends(get_current_admin_user)
# ):
#     """주문 상태 변경"""
#     order = order_crud.get_order(session, order_id)
#     if not order:
#         raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")

#     try:
#         new_status = OrderStatus(status)
#     except ValueError:
#         raise HTTPException(status_code=400, detail="잘못된 상태입니다")

#     order_crud.update_order_status(session, order, new_status)

#     return RedirectResponse(url=f"/admin/orders/{order_id}", status_code=303)
