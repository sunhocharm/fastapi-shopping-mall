from app.config import settings
from fastapi.responses import Response


def _set_token_in_cookie(response: Response, _key: str, _token: str, _max_age: int) -> None:
    response.set_cookie(
        key=_key,
        value=_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=_max_age
    )


def _delete_token_in_cookie(response: Response, _key: str) -> None:
    response.set_cookie(key=_key, httponly=True, secure=True, samesite="lax", expires=0, max_age=0)


def _set_access_token_in_cookie(response: Response, access_token: str) -> None:
    _max_age = settings.access_token_expire_minutes * 60
    _set_token_in_cookie(response, _key="access_token", _token=access_token, _max_age=_max_age)


def _set_refresh_token_in_cookie(response: Response, refresh_token: str) -> None:
    _max_age = settings.refresh_token_expire_days * 24 * 60 * 60
    _set_token_in_cookie(response, _key="refresh_token", _token=refresh_token,  _max_age=_max_age)


def set_access_and_refresh_token_in_cookie(response: Response, access_token: str, refresh_token: str) -> None:
    _set_access_token_in_cookie(response, access_token)
    _set_refresh_token_in_cookie(response, refresh_token)


def delete_access_and_refresh_token_in_cookie(response: Response) -> None:
    _delete_token_in_cookie(response, "access_token")
    _delete_token_in_cookie(response, "refresh_token")


def set_cart_session_token_in_cookie(response: Response, session_id: str) -> None:
    _max_age = settings.cart_session_token_expire_days * 24 * 60 * 60
    response.set_cookie(
        key="cart_session",
        value=session_id,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=_max_age
    )


def delete_cart_session_token_in_cookie(response: Response) -> None:
    response.set_cookie(key="cart_session", httponly=True, secure=True, samesite="strict", expires=0, max_age=0)
