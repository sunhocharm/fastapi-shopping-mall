from app.config import settings
from datetime import datetime

from fastapi import Request

# from fastapi.templating import Jinja2Templates
from app.dependencies import get_templates

from tzlocal import get_localzone
from zoneinfo import ZoneInfo




APP_TIME_ZONE = get_localzone()


def format_price(value: int) -> str:
    """가격 포맷 (1000 -> 1,000)"""
    return f"{value:,}"


def format_date(value: datetime) -> str:
    """날짜만"""
    return format_datetime(value, "%Y-%m-%d")


def format_datetime(value: datetime, format: str = "%Y-%m-%d %H:%M") -> str:
    """날짜 포맷"""
    if not value:
        return ""
    
    if (value.tzinfo is not None) and (value.tzinfo.utcoffset(value) is not None):
        return (value.astimezone(ZoneInfo(APP_TIME_ZONE.key))).strftime(format)

    return value.strftime(format)


def status_text(status) -> str:
    texts = {
        "pending": "결제 대기",
        "paid": "결제 완료",
        "preparing": "배송 준비",
        "shipping": "배송 중",
        "delivered": "배송 완료",
        "cancelled": "취소됨"
    }
    val = status.value if hasattr(status, 'value') else status
    return texts.get(val, val)


def status_badge(status) -> str:
    badges = {
        "pending": "bg-warning text-dark",
        "paid": "bg-success",
        "preparing": "bg-info",
        "shipping": "bg-primary",
        "delivered": "bg-secondary",
        "cancelled": "bg-danger"
    }
    val = status.value if hasattr(status, 'value') else status
    return badges.get(val, "bg-secondary")


# def setup_jinja2_filters(_templates: Jinja2Templates) -> None:
def setup_jinja2_filters() -> None:
    _templates = get_templates()
    _templates.env.filters["format_price"] = format_price
    _templates.env.filters["format_date"] = format_date
    _templates.env.filters["format_datetime"] = format_datetime
    _templates.env.filters["status_text"] = status_text
    _templates.env.filters["status_badge"] = status_badge

    _templates.env.globals["site_name"] = settings.site_name
    # _templates.env.globals["cart_count"] = 0

    # 1. 컨텍스트 프로세서로 동작할 함수를 정의합니다.
    def auth_context(request: Request):
        return {
            "current_user": getattr(request.state, "user", None),
            "cart_total": getattr(request.state, "cart_total", None)
        }

    _templates.context_processors.append(auth_context)
