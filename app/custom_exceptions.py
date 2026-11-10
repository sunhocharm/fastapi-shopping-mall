from fastapi import status


class PossibleHackingError(Exception):
    pass


class BaseBusinessError(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "서버 내부 오류가 발생하였습니다."

    def __init__(self, detail: str | None = None, status_code: int | None = None) -> None:
        if detail:
            self.detail = detail

        if status_code:
            self.status_code = status_code

        super().__init__(self.detail)


class EntityNotFoundError(BaseBusinessError):
    status_code: int = status.HTTP_404_NOT_FOUND
    detail: str = "요청하신 데이터를 찾을 수 없습니다."


class EntityAlreadyExistsError(BaseBusinessError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "이미 존재하는 데이터입니다."


class CustomPermissionError(BaseBusinessError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "이 작업을 수행할 권한이 없습니다."


class CustomBadRequestError(BaseBusinessError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "잘못된 요청입니다."


class CustomCredentialError(BaseBusinessError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid or expired token."


class DatabaseConstraintError(BaseBusinessError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "데이터베이스 제약 조건 위반 오류가 발생했습니다."


class CustomDatabaseError(BaseBusinessError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "데이터베이스 오류가 발생했습니다."


# --------------------------------------------------------------------------- #
# --- 여기서 부터 사이트 별 custom error 추가한다 ------------------------------- #
# --------------------------------------------------------------------------- #
class CartValidationError(BaseBusinessError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "상품이 존재하지 않습니다"
    def __init__(self, errors: list[dict]):
        result = "\n".join(errors)
        self.detail = result
        super().__init__(result)
