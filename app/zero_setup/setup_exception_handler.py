from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler

from app.custom_exceptions import BaseBusinessError

from loguru import logger


templates = Jinja2Templates(directory="templates")


def template_response_with_error_message(
        request: Request, 
        status_code: int, 
        msg: str
) -> Jinja2Templates.TemplateResponse:
    return templates.TemplateResponse(
        request=request,
        name="errors/404.html",
        status_code=status_code,
        context={
            "status_code": status_code,
            "title": status_code,
            "message": msg
        }
    )

async def base_business_error(request: Request, exc: BaseBusinessError):
    msg = exc.detail
    status_code = exc.status_code

    logger.error(
        f"BaseBusinessError [{status_code}] - URL: [{request.url.path}] | Method: [{request.method}] | Message: [{msg}]"
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=status_code, content={"detail": msg})

    return template_response_with_error_message(request, status_code, msg)


async def general_http_exception_handler(request: Request, exc: StarletteHTTPException):
    msg = exc.detail or "An error occurred. Please check your request and try again."
    status_code = exc.status_code

    logger.error(
        f"StarletteHTTPException [{status_code}] - URL: [{request.url.path}] | Method: [{request.method}] | Message: [{msg}]"
    )

    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exc)

    return template_response_with_error_message(request, status_code, msg)


async def req_validation_exception_handler(request: Request, exc: RequestValidationError):

    # msg_list = [str({ "field": ".".join(str(x) for x in error["loc"]), "message": error["msg"] }) for error in exc.errors()]
    # msg = "\n".join(msg_list)

    # errors = []
    # for error in exc.errors():
    #     errors.append({ "field": ".".join(str(x) for x in error["loc"]), "message": error["msg"] })
    # # return JSONResponse(
    # #     status_code=422,
    # #     content={"errors": errors}
    # # )

    msg = "입력 데이터 오류(유효성 검증 실패)입니다."
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT

    logger.error(
        f"RequestValidationError [{status_code}] - URL: [{request.url.path}] | Method: [{request.method}] | Message: [{msg}]"
    )

    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exc)

    return template_response_with_error_message(request, status_code, msg)


async def internal_server_error(request: Request, exc: Exception):
    status_code = getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR)
    msg = getattr(exc, "detail", "서버 내부 오류가 발생했습니다. 관리자에게 문의하세요.")

    logger.error(
        f"internal_server_error [{status_code}] - URL: [{request.url.path}] | Method: [{request.method}] | Message: [{str(exc)}]"
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=status_code, content={"detail": msg})

    return template_response_with_error_message(request, status_code, msg)


# --- 메인 앱에서 호출할 등록 함수 ---
def setup_exception_handlers(_app: FastAPI) -> None:
    """FastAPI 인스턴스에 예외 핸들러들을 등록합니다."""
    _app.add_exception_handler(BaseBusinessError, base_business_error)
    _app.add_exception_handler(StarletteHTTPException, general_http_exception_handler)
    _app.add_exception_handler(RequestValidationError, req_validation_exception_handler)
    _app.add_exception_handler(Exception, internal_server_error)
