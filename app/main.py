from app.config import settings

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse


from app.database import engine
from contextlib import asynccontextmanager
# from sqlmodel import text

from loguru import logger
from app.dependencies import TemplatesDep 
from app.zero_setup import (
    setup_logger, setup_middlewares, setup_exception_handlers, setup_mount_point, setup_jinja2_filters
)

from app import db_models # noqa: F401

from app.dependencies import CurrentUserOptional
from app.dependency.category_dep import CategoryServiceDep
from app.dependency.product_dep import ProductServiceDep

# --- start: router ---------------------------------------------------------------- #
from app.router.mypage_router import router as mypage_router
from app.router.products_router import router as products_router
from app.router.auth_router import router as user_auth_router
from app.router.cart_api_router import router as cart_api_router
from app.router.cart_router import router as cart_router
from app.router.checkout_router import router as checkout_router
from app.router.order_router import router as order_router
from app.router.payment_router import router as payment_router

from app.router.admin.dashboard_router import router as admin_dashboard_router
from app.router.admin.auth_router import router as admin_auth_router
from app.router.admin.category_router import router as admin_category_router
from app.router.admin.product_router import router as admin_product_router
from app.router.admin.order_router import router as admin_order_router
# --- end: router ------------------------------------------------------------------ #



setup_logger()


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    logger.info("\n\n\t[[ Application Startup ]]\n\n")
    yield
    logger.info("\n\n\t[[ Application Shutdown ]]\n\n")
    await engine.dispose()


IS_PRODUCT_MODE = True if settings.is_product_mode else False

app = FastAPI(
    title="Shopping App", 
    lifespan=_lifespan,
    docs_url=None if IS_PRODUCT_MODE else "/docs",
    redoc_url=None if IS_PRODUCT_MODE else "/redoc",
    openapi_url=None if IS_PRODUCT_MODE else "/openapi.json",
)

setup_middlewares(app)
setup_exception_handlers(app)
setup_jinja2_filters()
setup_mount_point(app)


def _setup_routers(_app: FastAPI) -> None:
    _app.include_router(mypage_router, prefix="/mypage", tags=["mypage"])
    _app.include_router(products_router, prefix="/products", tags=["products"])
    _app.include_router(user_auth_router, prefix="", tags=["auth"])
    _app.include_router(cart_router, prefix="/cart", tags=["cart-page"])
    _app.include_router(cart_api_router, prefix="/api/cart", tags=["cart-api"])
    _app.include_router(checkout_router, prefix="/checkout", tags=["checkout"])
    _app.include_router(order_router, prefix="/orders", tags=["orders"])
    _app.include_router(payment_router, prefix="/payment", tags=["payment"])

    _app.include_router(admin_order_router, prefix="/admin/orders", tags=["admin-orders"])
    _app.include_router(admin_product_router, prefix="/admin/products", tags=["admin-products"])
    _app.include_router(admin_category_router, prefix="/admin/categories", tags=["admin-categories"])
    _app.include_router(admin_auth_router, prefix="/admin", tags=["admin-auth"])
    _app.include_router(admin_dashboard_router, prefix="/admin", tags=["admin-dashboard"])

_setup_routers(app)


@app.get("/", include_in_schema=False, response_class=HTMLResponse)
async def home(
    request: Request,
    category_service: CategoryServiceDep,
    product_service: ProductServiceDep,
    current_user: CurrentUserOptional,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ home ]]\n\n")

    categories = await category_service.get_all_categories()
    featured_products = await product_service.get_all_products(featured_only=True, limit=4)

    return templates.TemplateResponse(
        request, name="index.html", context={
            "categories": categories, "featured_products": featured_products
        }
    )
