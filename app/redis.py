from app.config import settings
import redis.asyncio as async_redis


# 전역 Redis 클라이언트
redis_client: async_redis.Redis | None = None


async def get_redis() -> async_redis.Redis:
    """Redis 클라이언트를 반환합니다."""
    global redis_client
    if redis_client is None:
        redis_client = async_redis.from_url(settings.redis_url, encoding="UTF-8", decode_responses=True, protocol=2)
    return redis_client


async def close_redis() -> None:
    """Redis 연결을 종료합니다."""
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        redis_client = None
