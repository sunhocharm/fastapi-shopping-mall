from functools import lru_cache
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="UTF-8",
        extra="ignore"
    )

    is_product_mode: bool

    site_name: str ="FastAPI Shop"

    profile_pics_dir: str = "media/profile_pics"
    jwt_algorithm: str = "HS256"

    database_url: str

    access_token_secret_key: SecretStr
    refresh_token_secret_key: SecretStr

    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14
    cart_session_token_expire_days: int = 1

    # 주문서형·결제창형 연동 키 - 주문서형·결제창형 결제를 연동할 때 사용해요
    toss_client_key: SecretStr          # for frontend
    toss_secret_key: SecretStr          # for backend

    upload_dir: str
    do_create_product_thumbnail: bool = True
    product_image_thumbnail_size: tuple[int, int] = (300, 300)
    max_upload_size_bytes: int
    # max_upload_size_mbs: int = max_upload_size_bytes / (1024 * 1024)


    frontend_url: str

    mail_server: str
    mail_port: int
    mail_username: str
    mail_password: SecretStr
    mail_from: str
    mail_use_tls: bool

    google_client_id: str
    google_client_secret: SecretStr
    google_redirect_uri: str

    github_client_id: str
    github_client_secret: SecretStr
    github_redirect_uri: str

    kakao_client_id: str
    kakao_client_secret: SecretStr
    kakao_redirect_uri: str


@lru_cache
def get_settings() -> Settings:
    return Settings()   # type: ignore[call-arg]


settings = get_settings()
