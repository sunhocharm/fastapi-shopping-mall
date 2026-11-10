from fastapi import APIRouter, Request
from loguru import logger
from app.dependencies import TemplatesDep


router = APIRouter() # (prefix="/admin", tags=["admin-dashboard"])


@router.get("")
async def admin_dashboard(
    request: Request,
    templates: TemplatesDep
):
    logger.info("\n\n\t[[ admin_dashboard ]]\n\n")

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
    )
