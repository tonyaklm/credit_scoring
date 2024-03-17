from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
import typer
import asyncio

# DATABASE_URL = "postgresql+asyncpg://product_engine:product_engine@postgresql:5432/product_engine"
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@postgresql:5432/product_engine"

engine = create_async_engine(DATABASE_URL, echo=True)
Base = sqlalchemy.orm.declarative_base()
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_models():
    """Initializing models"""
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def pe_get_session() -> AsyncSession:
    """Getting async session"""
    async with async_session() as session:
        yield session


cli = typer.Typer()


@cli.command()
def db_init_models():
    asyncio.run(init_models())