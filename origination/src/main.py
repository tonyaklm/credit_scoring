import random

import sqlalchemy
from fastapi import Depends
from fastapi import Request, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from flask_restful.representations import json
from pydantic import BaseModel
from sqlalchemy import select, delete, Column, Integer, Float, \
    VARCHAR, PrimaryKeyConstraint, UniqueConstraint, ForeignKeyConstraint, Index, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError, DBAPIError
from datetime import date, datetime
import asyncio
import typer
import pytz

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# PRODUCT_ENGINE_URL = "postgresql+asyncpg://product_engine:product_engine@postgresql:5432/product_engine"
# ORIGINATION_URL = "postgresql+asyncpg://product_engine:product_engine@postgresql:5432/origination"

PRODUCT_ENGINE_URL = "postgresql+asyncpg://postgres:postgres@postgresql:5432/product_engine"
ORIGINATION_URL = "postgresql+asyncpg://postgres:postgres@postgresql:5432/origination"

pe_engine = create_async_engine(PRODUCT_ENGINE_URL, echo=True)
PE_Base = sqlalchemy.orm.declarative_base()
pe_async_session = sessionmaker(
    pe_engine, class_=AsyncSession, expire_on_commit=False
)

origination_engine = create_async_engine(ORIGINATION_URL, echo=True)
Origination_Base = sqlalchemy.orm.declarative_base()
origination_async_session = sessionmaker(
    origination_engine, class_=AsyncSession, expire_on_commit=False
)


async def init_models():
    """Initializing models"""
    async with pe_engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(PE_Base.metadata.create_all)

    async with origination_engine.begin() as conn:
        await conn.run_sync(Origination_Base.metadata.create_all)


class Application(Origination_Base):
    __tablename__ = 'application'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, nullable=False)
    product_code = Column(VARCHAR, nullable=False)
    status = Column(VARCHAR, nullable=False)
    time_of_application = Column(sqlalchemy.types.DateTime(timezone=True), nullable=False)
    disbursment_amount = Column(Float, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='application_pkey'),
        Index('client_id_index' 'client_id'),
        # Index('product_index' 'product_code')
    )


class Product(PE_Base):
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


class Client(PE_Base):
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


class Agreement(PE_Base):
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


class ApplicationSchema(BaseModel):
    application_id: int


async def pe_get_session() -> AsyncSession:
    """Getting async session Project Engine"""
    async with pe_async_session() as session:
        yield session


async def origination_get_session() -> AsyncSession:
    """Getting async session Origination"""
    async with origination_async_session() as session:
        yield session


cli = typer.Typer()


@cli.command()
def db_init_models():
    asyncio.run(init_models())
    print("Done")


class Repository:

    async def select_by_criteria(self, table, columns: list, values: list, session: AsyncSession,
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

    async def select_all(self, table, session: AsyncSession) -> json:
        """Makes select all available items"""

        stmt = select(table)
        results = await session.execute(stmt)
        response_json = results.scalars().all()
        return response_json

    async def post_item(self, table, item: json, session: AsyncSession) -> Integer:
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

    async def delete_item(self, table, column: str, value, session: AsyncSession):
        """Deletes item by criteria from given table"""
        stmt = delete(table).where(getattr(table, column) == value)
        results = await session.execute(stmt)
        deleted_rows_count = results.rowcount
        await session.commit()
        if deleted_rows_count == 0:
            raise HTTPException(status_code=404, detail="Объекта не существует")

    async def update_item(self, table: PE_Base, column: str, value, changed_column: str, new_value,
                          session: AsyncSession):
        try:
            stmt = update(table).where(getattr(table, column) == value).values({changed_column: new_value})
            await session.execute(stmt)
            await session.commit()
        except DataError:
            raise HTTPException(status_code=404, detail="Объекта не существует")
        print('OK')


repo = Repository()


def calculateAge(birth_date_str: str) -> int:
    """Calculates age from birthdate til now"""
    birth_date = datetime.strptime(birth_date_str, '%d.%m.%Y')
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age


@app.post("/application", status_code=200, summary="Set new application", response_model=ApplicationSchema)
async def post_application(request: Request, session: AsyncSession = Depends(origination_get_session)
                           , pe_session: AsyncSession = Depends(pe_get_session)):
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

    results_json = await repo.select_by_criteria(Client, names, values, pe_session,
                                                 raise_error=False)

    if not results_json:
        client_id = await repo.post_item(Client, {'client_name': client_name,
                                                  'client_age': calculate_age,
                                                  'client_phone_number': item['phone'],
                                                  'client_passport_number': item['passport_number'],
                                                  'client_salary': item['salary']
                                                  }, pe_session)
    else:
        print(results_json)
        client_id = results_json.id

    product_code = str(item['product_code'])

    application_names = ['client_id', 'product_code']
    application_values = [client_id, product_code]

    results_json = await repo.select_by_criteria(Application, application_names, application_values, session,
                                                 raise_error=False)
    moscow_tz = pytz.timezone("Europe/Moscow")
    time_of_application = datetime.now(moscow_tz)

    print(type(product_code))

    new_item = {'client_id': client_id,
                'product_code': product_code,
                'time_of_application': time_of_application,
                'disbursment_amount': item['disbursment_amount'],
                'status': 'new'
                }
    if results_json and (results_json.disbursment_amount == item['disbursment_amount'] or (
            results_json.time_of_application - time_of_application).days < 7):
        # совпадение по полям или меньше 7 дней с прошлой заявки на этот же продукт
        application_id = results_json.id
        try:
            await repo.update_item(Application, 'id', application_id, 'status', 'closed', session)
        except HTTPException:
            raise HTTPException(status_code=404, detail="Объекта не существует")
        JSONResponse(status_code=409, content={"application_id": application_id})
    else:
        application_id = await repo.post_item(Application, new_item, session)

    return {"application_id": application_id}


@app.post("/application/{application_id}/close", status_code=204, summary="Delete application by its id")
async def close_application(application_id, session: AsyncSession = Depends(pe_get_session)):
    try:
        await repo.update_item(Application, 'id', application_id, 'status', 'closed', session)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Объекта не существует")


if __name__ == "__main__":
    cli()
