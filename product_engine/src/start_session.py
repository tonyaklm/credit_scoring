from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings

engine = create_async_engine(settings.database_url, echo=True)
Base = sqlalchemy.orm.declarative_base()
product_engine_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def pe_get_session() -> AsyncSession:
    """Getting async session"""
    async with product_engine_session() as session:
        yield session
