import random

import sqlalchemy
from fastapi import Depends
from fastapi import Request, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from flask_restful.representations import json
from pydantic import BaseModel
from sqlalchemy import select, delete, Column, Integer, Float, \
    VARCHAR, PrimaryKeyConstraint, UniqueConstraint, ForeignKeyConstraint, Index
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError, DBAPIError
from datetime import date, datetime
import pytz
import asyncio
import typer

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker


app = FastAPI()

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


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    title = Column(VARCHAR, nullable=False)
    code = Column(VARCHAR, nullable=False, unique=True)
    min_term = Column(Integer, nullable=False)
    max_term = Column(Integer, nullable=False)
    min_principal = Column(Float, nullable=False)
    max_principal = Column(Float, nullable=False)
    min_interest = Column(Float, nullable=False)
    max_interest = Column(Float, nullable=False)
    min_origination = Column(Float, nullable=False)
    max_origination = Column(Float, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='product_pkey'),
        UniqueConstraint('code'),
        Index('code_index' 'code')
    )


class ProductSchema(BaseModel):
    id: int
    title: str
    code: str
    min_term: int
    max_term: int
    min_principal: float
    max_principal: float
    min_interest: float
    max_interest: float
    min_origination: float
    max_origination: float


class Client(Base):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True)
    client_name = Column(VARCHAR, nullable=False)
    client_age = Column(Integer, nullable=False)
    client_phone_number = Column(VARCHAR, nullable=False)
    client_passport_number = Column(VARCHAR, nullable=False)
    client_salary = Column(Float, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='client_pkey'),
        Index('passport_index' 'client_passport_number'),
        Index('phone_index' 'client_phone_number'),
        Index('client_name' 'client_name')
    )


class Agreement(Base):
    __tablename__ = 'agreement'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, nullable=False)
    client_id = Column(Integer, nullable=False)
    term = Column(Integer, nullable=False)
    principal = Column(Float, nullable=False)
    interest = Column(Float, nullable=False)
    origination = Column(Float, nullable=False)
    activation_time = Column(sqlalchemy.types.DateTime(timezone=True), nullable=False)
    status = Column(VARCHAR, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='agreement_pkey'),
        Index('product_index' 'product_id'),
        Index('client_index' 'client_id'),
        ForeignKeyConstraint(['product_id'], ['product.id']),
        ForeignKeyConstraint(['client_id'], ['client.id'])
    )


class AgreementSchema(BaseModel):
    agreement_id: int


async def get_session() -> AsyncSession:
    """Getting async session"""
    async with async_session() as session:
        yield session


cli = typer.Typer()


@cli.command()
def db_init_models():
    asyncio.run(init_models())
    print("Done")


class Repository:

    async def select_by_criteria(self, table: Base, columns: list, values: list, session: AsyncSession,
                                 raise_error=True, code_error=404) -> json:
        """Makes select by given column names and expected values"""

        items = select(table).where(getattr(table, columns[0]) == values[0])
        for i in range(1, len(columns)):
            items = items.where(getattr(table, columns[i]) == values[i])
        results = await session.execute(items)
        response_json = results.scalars().all()
        if not response_json and raise_error:
            raise HTTPException(status_code=code_error, detail="Объекта не существует")
        if not response_json:
            return {}
        return response_json[0]

    async def select_all(self, table: Base, session: AsyncSession) -> json:
        """Makes select all available items"""

        stmt = select(table)
        results = await session.execute(stmt)
        response_json = results.scalars().all()
        return response_json

    async def post_item(self, table: Base, item: json, session: AsyncSession) -> Integer:
        """Posts new item into given table"""
        try:
            new_item = table(**item)
            session.add(new_item)
            await session.commit()
        except IntegrityError:
            raise HTTPException(status_code=409, detail="Объект уже существует")
        except DBAPIError or DataError:
            print(item)
            raise HTTPException(status_code=400, detail="Переданы неверные данные")
        return new_item.id

    async def delete_item(self, table: Base, column: str, value, session: AsyncSession):
        """Deletes item by criteria from given table"""
        stmt = delete(table).where(getattr(table, column) == value)
        results = await session.execute(stmt)
        deleted_rows_count = results.rowcount
        await session.commit()
        if deleted_rows_count == 0:
            raise HTTPException(status_code=404, detail="Объекта не существует")


repo = Repository()


def calculateAge(birth_date_str: str) -> int:
    """Calculates age from birthdate til now"""
    birth_date = datetime.strptime(birth_date_str, '%d.%m.%Y')
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age


def check_between(min_value, max_value, real_value) -> bool:
    """Checks if value in given interval"""
    try:
        return min_value <= real_value <= max_value
    except TypeError:
        return False


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/product", status_code=200, summary="Get all products", response_model=list[ProductSchema])
async def get_products(session: AsyncSession = Depends(get_session)):
    resp = await repo.select_all(Product, session)
    return resp


@app.post("/product", status_code=200, summary="Set new product")
async def post_product(request: Request, session: AsyncSession = Depends(get_session)):
    item = await request.json()
    await repo.post_item(Product, item, session)


@app.post("/agreement", status_code=200, summary="Set agreement by it's client and product",
          response_model=AgreementSchema)
async def post_agreement(request: Request, session: AsyncSession = Depends(get_session)):
    item = await request.json()
    try:
        client_name = ' '.join([item['first_name'], item['second_name'], item['third_name']])
    except TypeError:
        return JSONResponse(status_code=400, content={
            "message": f"Неверный формат данных"})

    if type(item['birthday']) != str:
        return JSONResponse(status_code=400, content={
            "message": f"Неверный формат данных"})
    calculate_age = calculateAge(item['birthday'])

    names = ['client_name', 'client_age', 'client_phone_number', 'client_passport_number', 'client_salary']
    values = [client_name, calculate_age, item['phone'], item['passport_number'], item['salary']]

    results_json = await repo.select_by_criteria(Client, names, values, session,
                                                 raise_error=False)

    if not results_json:
        client_id = await repo.post_item(Client, {'client_name': client_name,
                                                  'client_age': calculate_age,
                                                  'client_phone_number': item['phone'],
                                                  'client_passport_number': item['passport_number'],
                                                  'client_salary': item['salary']
                                                  }, session)
    else:
        print(results_json)
        client_id = results_json.id

    # ищу продукт

    response_json = await repo.select_by_criteria(Product, ['code'], [item['product_code']], session, code_error=400)
    product_id = response_json.id

    min_origination = response_json.min_origination
    max_origination = response_json.max_origination

    origination_amount = random.uniform(min_origination, max_origination)
    principal_amount = item['disbursment_amount'] + origination_amount

    min_term = response_json.min_term
    max_term = response_json.max_term

    if not check_between(min_term, max_term, item['term']):
        return JSONResponse(status_code=400, content={
            "message": f"Срок кредита должен составлять от {min_term} до {max_term} месяцев"})

    if not check_between(min_origination, max_origination, origination_amount):
        return JSONResponse(status_code=400, content={
            "message": f"Размер комиссии должен составлять от {min_origination} до {max_origination} руб"})

    min_interest = response_json.min_interest
    max_interest = response_json.max_interest
    if not check_between(min_interest, max_interest, item['interest']):
        return JSONResponse(status_code=400, content={
            "message": f"Размер процентной ставки должен составлять от {min_interest} до {max_interest} %"})

    min_principal = response_json.min_principal
    max_principal = response_json.max_principal
    if not check_between(min_principal, max_principal, principal_amount):
        return JSONResponse(status_code=400, content={
            "message": f"Сумма кредита должна составлять от {min_principal} до {max_principal} руб"})
    moscow_tz = pytz.timezone("Europe/Moscow")
    agreement_id = await repo.post_item(Agreement, {'product_id': product_id,
                                                    'client_id': client_id,
                                                    'term': item['term'],
                                                    'principal': principal_amount,
                                                    'interest': item['interest'],
                                                    'origination': origination_amount,
                                                    'activation_time': datetime.now(moscow_tz),
                                                    'status': 'New',
                                                    }, session)
    return {"agreement_id": agreement_id}


@app.delete("/product/{product_code}", status_code=204, summary="Delete product by it's code")
async def delete_by_product_name(product_code, session: AsyncSession = Depends(get_session)):
    await repo.delete_item(Product, 'code', product_code, session)


@app.get("/product/{product_code}", status_code=200, summary="Get product by it's code", response_model=ProductSchema)
async def get_by_product_code(product_code, session: AsyncSession = Depends(get_session)):
    return await repo.select_by_criteria(Product, ['code'], [product_code], session)


@app.get("/hello/{name}", summary="Say hi")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


if __name__ == "__main__":
    cli()
