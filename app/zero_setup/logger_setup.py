from app.config import settings
from loguru import logger

from pathlib import Path
import sys


IS_PROD_MODE: bool = True if settings.is_product_mode else False

def setup_logger() -> None:
    # 1. Loguru 기본 설정 (콘솔 출력 포맷 및 파일 저장 설정)
    logger.remove()  # 기본 핸들러 제거 (중복 출력 방지)
    logger_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    # logger_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <magenta>[{extra[request_id]:-}]</magenta> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    if not IS_PROD_MODE:
        logger.add(sys.stdout, format=logger_format, level="INFO")

    if IS_PROD_MODE:
        logger.add(
            Path("./logs/server.log"),  # Path("D:\\sunho_park\\log\\server.log"),
            rotation="10 MB",     # 10MB 단위로 로그 파일 로테이션
            retention="10 days",  # 10일간 보관
            level="ERROR",        # 파일에는 ERROR 이상만 기록
            format=logger_format,
            encoding="UTF-8"
        )
