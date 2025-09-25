from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
import asyncio
from contextlib import asynccontextmanager
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from scout.db.models import Base



engine = create_async_engine("sqlite+aiosqlite:///./db/scout.db",echo=True)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)



async def create_tables():
    async with engine.begin() as conn: 
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_fastapi_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


def get_session() -> AsyncSession:
    return async_session_factory()
    
 


if __name__ == "__main__":
    asyncio.run(create_tables())