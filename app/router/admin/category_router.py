from loguru import logger
from typing import Annotated

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from app.dependencies import TemplatesDep, CurrentAdminUser
from app.dependency.category_dep import CategoryServiceDep
from app.schema.product_schema import CategoryCreate

router = APIRouter()    # prefix="/admin/categories", tags=["admin-categories"]


# ------------------------------------------------------- #
# --- get all categories -------------------------------- #
@router.get("")
async def get_all_categories(
    request: Request, 
    category_service: CategoryServiceDep,
    admin: CurrentAdminUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ get_all_categories ]]\n\n")

    categories = await category_service.get_all_categories(active_only=False)

    return templates.TemplateResponse(
        request=request,
        name="admin/categories/list.html",
        context={"categories": categories}
    )

# ------------------------------------------------------- #
# --- page: create category page ------------------------ #
@router.get("/new")
async def create_category_page(
    request: Request, 
    admin: CurrentAdminUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ create_category_page ]]\n\n")

    return templates.TemplateResponse(
        request=request,
        name="admin/categories/form.html",
        context={"category": None}
    )

# ------------------------------------------------------- #
# --- create category ----------------------------------- #
@router.post("/new")
async def create_category(
    request: Request,
    req_data: Annotated[CategoryCreate, Form()],
    category_service: CategoryServiceDep,
    admin: CurrentAdminUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ create_category ]]\n\n")

    req_dict = req_data.model_dump()
    try:
        await category_service.create_category(req_dict)
    except Exception as err:
        return templates.TemplateResponse(
            request=request,
            name="admin/categories/form.html",
            context={ "category": req_dict, "server_errors": str(err) }
        )

    return RedirectResponse(url="/admin/categories", status_code=303)

# ------------------------------------------------------- #
# --- page: edit category page -------------------------- #
@router.get("/{category_id}/edit")
async def edit_category_page(
    request: Request,
    category_id: int,
    category_service: CategoryServiceDep,
    admin: CurrentAdminUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ edit_category_page ]]\n\n")
    
    category = await category_service.get_category_by_id(category_id)

    if not category:
        return RedirectResponse(url="/admin/categories", status_code=303)
    
    category_dump = category.model_dump(mode="json")
    return templates.TemplateResponse(
        request=request,
        name="admin/categories/form.html",
        context={"category": category_dump}
    )


# ------------------------------------------------------- #
# --- edit category ------------------------------------- #
@router.post("/{category_id}/edit")
async def edit_category(
    request: Request,
    category_id: int,
    req_data: Annotated[CategoryCreate, Form()],
    category_service: CategoryServiceDep,
    admin: CurrentAdminUser,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ edit_category ]]\n\n")
    
    req_dict = req_data.model_dump()
    try:
        await category_service.update_category(category_id, req_dict)
    except Exception as err:
        return templates.TemplateResponse(
            request=request,
            name="admin/categories/form.html",
            context={
                "category": req_dict,
                "server_errors": str(err)
            }
        )

    return RedirectResponse(url="/admin/categories", status_code=303)


# ------------------------------------------------------- #
# --- delete category ----------------------------------- #
@router.post("/{category_id}/delete")
async def delete_category(
    category_id: int,
    category_service: CategoryServiceDep,
    admin: CurrentAdminUser,
):
    logger.info("\n\n\t[[ delete_category ]]\n\n")

    await category_service.delete_category(category_id)

    return RedirectResponse(url="/admin/categories", status_code=303)
