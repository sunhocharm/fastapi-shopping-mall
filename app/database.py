from app.config import settings

from typing import Annotated
from fastapi import Depends

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession


if settings.is_product_mode:
    engine = create_async_engine(
        url=settings.database_url, 
        echo=False,             # 개발 환경에서 SQL 로그 출력 (운영 환경에서는 False 권장)
        pool_size=20,           # 커넥션 풀 크기
        max_overflow=10,        # 풀이 가득 찼을 때 추가할 최대 커넥션 수
        pool_timeout=30,        # 커넥션을 얻기 위해 대기하는 최대 시간(초)
        pool_recycle=1800,      # 30분마다 커넥션 재연결 (서버측 끊김 방지)
    )
else:
    engine = create_async_engine(
        url=settings.database_url, 
        echo=True,
    )


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
