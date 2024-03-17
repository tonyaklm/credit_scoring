from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
import typer
import asyncio

# ORIGINATION_URL = "postgresql+asyncpg://product_engine:product_engine@postgresql:5432/origination"
ORIGINATION_URL = "postgresql+asyncpg://postgres:postgres@postgresql:5432/origination"

origination_engine = create_async_engine(ORIGINATION_URL, echo=True)
Origination_Base = sqlalchemy.orm.declarative_base()
origination_async_session = sessionmaker(
    origination_engine, class_=AsyncSession, expire_on_commit=False
)


async def init_models():
    """Initializing models"""

    async with origination_engine.begin() as conn:
        await conn.run_sync(Origination_Base.metadata.create_all)


async def origination_get_session() -> AsyncSession:
    """Getting async session Origination"""
    async with origination_async_session() as session:
        yield session


cli = typer.Typer()


@cli.command()
def db_init_models():
    asyncio.run(init_models())
