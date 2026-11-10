from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi import Request
from app.dependencies import _get_current_user
from app.database import AsyncSessionLocal

from app.redis import get_redis
# import redis.asyncio as aioredis
from app.util.string_util import hash_token

from loguru import logger

redis_client = get_redis()

async def add_auth_user_middleware(request: Request, call_next):
    request.state.user = None
    request.state.cart_total = None

    # 1. 브라우저의 CORS Preflight(OPTIONS) 요청은 DB 조회 없이 통과
    if request.method == "OPTIONS":
        return await call_next(request)

    # 2. 정적 파일 및 업로드 파일 요청은 DB 조회 없이 조기 통과 (추가된 부분)
    # 2026년 표준 FastAPI 아키텍처에서 성능 최적화를 위한 필수 패턴입니다.
    if request.url.path.startswith(("/static", "/upload", "favicon")):
        return await call_next(request)

    access_token = request.cookies.get("access_token")
    cart_session_id = request.cookies.get("cart_session")


    # [핵심] Redis에서 cart_total 일괄 조회
    if cart_session_id:
        try:
            hashed_cart_session_id = hash_token(cart_session_id)
            redis_key = f"cart:total:{hashed_cart_session_id}"
            cached_total = await redis_client.get(redis_key)
            
            if cached_total is not None:
                request.state.cart_total = int(cached_total)
            else:
                # 만약 Redis 캐시가 날아갔다면 DB에서 조회 후 Redis에 다시 채워넣는 
                # 캐시 미스(Cache Miss) 방어 로직을 여기에 둘 수도 있습니다.
                request.state.cart_total = 0 
        except Exception as e:
            logger.error(f"Redis cart total error: {e}")


    if access_token:
        try:
            # async with를 통해 예외 발생 시에도 세션이 안전하게 닫히도록 보장
            async with AsyncSessionLocal() as session: 
                current_user = await _get_current_user(access_token, session)
                if current_user:
                    request.state.user = current_user
        except Exception as e:
            # DB 에러나 인증 에러로 인해 전체 서버가 멈추지 않도록 예외 처리 로그 남기기
            logger.error(f"Middleware auth error: {e}")
            # 필요에 따라 비로그인 처리(기본값 None) 유지 후 통과

    response = await call_next(request)
    return response


def _setup_cors_middleware(_app: FastAPI) -> None:
    origins = [ "http://localhost:3000", "http://127.0.0.1:3000" ]

    _app.add_middleware(
        CORSMiddleware, 
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # https://medium.com/@connect.hashblock/7-fastapi-security-patterns-that-actually-ship-19c52d717668
    # 7 FastAPI Security Patterns That Actually Ship

    # _app.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=["https://app.example.com"],
    #     allow_methods=["GET","POST","PUT","DELETE"],
    #     allow_headers=["authorization","content-type","x-csrf-token"],
    #     allow_credentials=True,
    # )

def setup_middlewares(_app: FastAPI) -> None:
    # FastAPI에서 미들웨어는 나중에 등록된 미들웨어가 먼저 실행(LIFO - Last In, First Out)됩니다.
    # 실행 순서: add_auth_user_middleware가 먼저 실행된 후 CORS 미들웨어가 실행됨
    _setup_cors_middleware(_app)
    _app.middleware("http")(add_auth_user_middleware)
