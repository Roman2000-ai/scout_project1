from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
import asyncio
from contextlib import asynccontextmanager


engine = create_async_engine("sqlite+aiosqlite:///db/scout.db")
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_fastapi_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


def get_session() -> AsyncSession:
    return async_session_factory()
    
 


