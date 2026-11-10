from loguru import logger
from typing import Annotated

from fastapi import APIRouter, Request, Form, UploadFile, File, status, HTTPException
from fastapi.responses import RedirectResponse
from app.dependencies import TemplatesDep, CurrentAdminUser
from app.dependency.product_dep import ProductServiceDep
from app.dependency.category_dep import CategoryServiceDep
from app.schema.product_schema import ProductCreate, ProductResponse

from app.service.file_upload_service import FileUploadService
from app.custom_exceptions import EntityNotFoundError


router = APIRouter()    # (prefix="/admin/products", tags=["admin-products"])


# ------------------------------------------------------- #
# --- get all products ---------------------------------- #
@router.get("")
async def get_all_products(
    request: Request, 
    product_service: ProductServiceDep,
    admin: CurrentAdminUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ get_all_categories ]]\n\n")

    products = await product_service.get_all_products()

    return templates.TemplateResponse(
        request=request,
        name="admin/products/list.html",
        context={"products": products}
    )


# ------------------------------------------------------- #
# --- form: create product_page ------------------------- #
@router.get("/new")
async def create_product_page(
    request: Request, 
    category_service: CategoryServiceDep,
    admin: CurrentAdminUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ create_product_page ]]\n\n")

    categories = await category_service.get_all_categories(active_only=True)

    return templates.TemplateResponse(
        request=request,
        name="admin/products/form.html",
        context={"product": None, "categories": categories}
    )


# ------------------------------------------------------- #
# --- create product ------------------------------------ #
@router.post("/new")
async def create_product(
    *,
    request: Request, 
    req_data: Annotated[ProductCreate, Form()],
    images: Annotated[list[UploadFile] | None, File()] = None,
    category_service: CategoryServiceDep,
    product_service: ProductServiceDep,
    admin: CurrentAdminUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ create_product ]]\n\n")

    product_dict = req_data.model_dump()

    # 브라우저 빈 파일 필터링 방어 코드
    valid_images = [img for img in images if img.filename] if images else None
    final_saved_paths = None
    file_service = FileUploadService()

    try:
        if valid_images and (len(valid_images) > 0):
            final_saved_paths = await file_service.save_image_files(valid_images, folder="products")
    except Exception as err:
        await file_service.remove_uploaded_files()

        categories = await category_service.get_all_categories(active_only=True)
        return templates.TemplateResponse(
            request=request, name="admin/products/form.html",
            context={"product": product_dict, "categories": categories, "server_errors": str(err)}
        )

    try:
        await product_service.create_product_with_files(product_dict, final_saved_paths)
    except Exception as err:
        await file_service.remove_uploaded_files()
        categories = await category_service.get_all_categories(active_only=True)
        return templates.TemplateResponse(
            request=request, name="admin/products/form.html",
            context={"product": product_dict, "categories": categories, "server_errors": str(err)}
        )

    return RedirectResponse(url="/admin/products", status_code=303)


# ------------------------------------------------------- #
# --- edit product_page --------------------------------- #
@router.get("/{product_id}/edit", response_model=ProductResponse)
async def edit_product_page(
    request: Request, 
    product_id: int,
    category_service: CategoryServiceDep,
    product_service: ProductServiceDep,
    admin: CurrentAdminUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ edit_product_page ]]\n\n")

    try:
        product = await product_service.get_product_category_images_by_product_id(product_id)
    except Exception:
        return RedirectResponse(url="/admin/products", status_code=303)

    validated_product = ProductResponse.model_validate(product)
    product_dump = validated_product.model_dump(mode="json")

    categories = await category_service.get_all_categories()
    return templates.TemplateResponse(
        request=request,
        name="admin/products/form.html",
        context={"product": product_dump, "categories": categories}
    )


# ------------------------------------------------------- #
# --- edit product -------------------------------------- #
@router.post("/{product_id}/edit")
async def edit_product(
    *,
    request: Request, 
    product_id: int,
    req_data: Annotated[ProductCreate, Form()],
    images: Annotated[list[UploadFile] | None, File()] = None,
    category_service: CategoryServiceDep,
    product_service: ProductServiceDep,
    admin: CurrentAdminUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ edit_product ]]\n\n")

    product_dict = req_data.model_dump()

    # 브라우저 빈 파일 필터링 방어 코드
    valid_images = [img for img in images if img.filename] if images else None

    product = await product_service.get_product_only_by_id(product_id)

    final_saved_paths = None
    file_service = FileUploadService()
    try:
        if valid_images and (len(valid_images) > 0):
            final_saved_paths = await file_service.save_image_files(valid_images, folder="products")
    except Exception as err:
        await file_service.remove_uploaded_files()

        categories = await category_service.get_all_categories(active_only=True)
        return templates.TemplateResponse(
            request=request, name="admin/products/form.html",
            context={"product": product_dict, "categories": categories, "server_errors": str(err)}
        )

    try:
        await product_service.update_product_with_files(product, product_dict, final_saved_paths)
    except Exception as err:
        await file_service.remove_uploaded_files()

        categories = await category_service.get_all_categories(active_only=True)
        return templates.TemplateResponse(
            request=request, name="admin/products/form.html",
            context={"product": product_dict, "categories": categories, "server_errors": str(err)}
        )

    return RedirectResponse(url="/admin/products", status_code=303)


# ------------------------------------------------------- #
# --- delete product ------------------------------------- #
@router.post("/{product_id}/delete")
async def delete_product(
    request: Request, 
    product_id: int,
    product_service: ProductServiceDep,
    admin: CurrentAdminUser,
):
    logger.info("\n\n\t[[ delete_product ]]\n\n")

    await product_service.delete_product(product_id)

    return RedirectResponse(url="/admin/products", status_code=303)


@router.post("/{product_id}/images/{image_id}/delete")
async def delete_product_image(
    request: Request, 
    product_id: int,
    image_id: int, 
    product_service: ProductServiceDep,
    admin: CurrentAdminUser,
):
    logger.info(f"\n\n\t[[ delete_product_image ]]\n\n")

    try:
        (file_full_path, thumbnail_file_full_path) = await product_service.delete_product_file(product_id, image_id)
        file_service = FileUploadService()
        await file_service.delete_uploaded_file(file_full_path, thumbnail_file_full_path)
    except Exception as err:
        return RedirectResponse(url=f"/admin/products/{product_id}/edit", status_code=303)

    return RedirectResponse(url=f"/admin/products/{product_id}/edit", status_code=303)


# 여러 개의 상품 이미지를 업로드받아 서버에 저장하는 엔드포인트
@router.post("/{product_id}/images")
async def upload_multiple_product_images(
    *,
    request: Request, 
    product_id: int,
    images: Annotated[list[UploadFile], File()],                    # 필수 처리
    # images: Annotated[list[UploadFile] | None, File()] = None,    # Optional 처리
    product_service: ProductServiceDep,
    admin: CurrentAdminUser,
):
    logger.info(f"\n\n\t[[ upload_multiple_product_images ]]\n\n")

    product = await product_service.get_product_only_by_id(product_id)
    if not product:
        raise EntityNotFoundError("상품을 찾을 수 없습니다")

    # 1. 전송된 파일이 비어있는지 확인
    if not images or images[0].size == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,  detail="업로드할 이미지 파일이 선택되지 않았습니다.")

    # 이미지 저장
    file_upload_service = FileUploadService()
    final_saved_paths: list[tuple[str, str]] = await file_upload_service.save_multiple_image(product_id, images, folder="products")
    await product_service.create_multiple_product_file_info(product, final_saved_paths)
    
    return RedirectResponse(url=f"/admin/products/{product_id}/edit", status_code=303)
