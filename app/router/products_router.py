from typing import Annotated
from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import RedirectResponse
from loguru import logger

from app.dependencies import TemplatesDep
from app.dependency.product_dep import ProductServiceDep
from app.dependency.category_dep import CategoryServiceDep

from app.schema.product_schema import ProductWithOneThumbImage


router = APIRouter()   # prefix="/products", tags=["products"]


@router.get("")
async def list_product(
    *,
    request: Request,
    category: Annotated[int | None, Query()] = None,
    query: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    category_service: CategoryServiceDep,
    product_service: ProductServiceDep,
    templates: TemplatesDep,
):
    logger.info("\n\n\t[[ list_product ]]\n\n")

    per_page = 3
    skip = (page - 1) * per_page

    categories = await category_service.get_all_categories()
    products = await product_service.get_all_products(query=query, category_id=category, skip=skip, limit=per_page)
    total = await product_service.get_count_for_all_products(query=query, category_id=category)
    total_pages = (total + per_page - 1) // per_page

    selected_category = None
    if category:
        selected_categories = [c for c in categories if c.id == category]
        if selected_categories and len(selected_categories) > 0: 
            selected_category = selected_categories[0]

    return templates.TemplateResponse(
        request=request,
        name="products/list.html",
        context={
            "products": products,
            "categories": categories,
            "selected_category": selected_category,
            "query": query,
            "page": page,
            "total_pages": total_pages,
            "total": total
        }
    )


@router.get("/{product_id}")
async def product_detail(
    *,
    request: Request,
    product_id: int, 
    page: Annotated[int, Query(ge=1)] = 1,
    product_service: ProductServiceDep,
    templates: TemplatesDep,
):
    logger.info("\n\n\t[[ product_detail ]]\n\n")

    product = await product_service.get_product_category_images_by_product_id(product_id)
    if not product:
        return templates.TemplateResponse(
            request=request, 
            name="errors/404.html", 
            context={
                "message": "관련 항목을 찾을 수 없습니다",
                "sub_message": f"[Product: {product_id}]",
                "back_url": "/products"
            }
        )

    # 관련 상품 (같은 카테고리)
    related_products = None
    if product.category_id:
        related_products: list[ProductWithOneThumbImage] = await product_service.get_products_by_category_id(product.category_id, product.id, limit=4)

    return templates.TemplateResponse(
        request=request,
        name="products/detail.html",
        context={
            "product": product,
            "related_products": related_products
        }
    )
