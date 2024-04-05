from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings

origination_engine = create_async_engine(settings.database_url, echo=True)
Origination_Base = sqlalchemy.orm.declarative_base()
origination_async_session = sessionmaker(
    origination_engine, class_=AsyncSession, expire_on_commit=False
)


async def origination_get_session() -> AsyncSession:
    """Getting async session Origination"""
    async with origination_async_session() as session:
        yield session
