from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import ssl
import os
import asyncpg

# (non-Docker) postgres
# DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/capture"

# Docker
# DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/capture"

# Heroku
DATABASE_URL = os.environ.get('DATABASE_URL')

ssl_object = ssl.create_default_context()
ssl_object.check_hostname = False
ssl_object.verify_mode = ssl.CERT_NONE
# connect elsewhere
pool = await asyncpg.create_pool(DATABASE_URL, ssl=ssl_object)

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
Base = declarative_base()


async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
