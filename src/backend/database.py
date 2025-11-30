from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# 환경 변수에서 DB URL 가져오기 (기본값 설정)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db/lerobot_db")

engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session
