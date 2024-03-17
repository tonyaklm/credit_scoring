import random

import sqlalchemy
from fastapi import Depends
from fastapi import Request, FastAPI, HTTPException
from fastapi.responses import JSONResponse
import json
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError, DBAPIError
from datetime import date, datetime
import pytz
import asyncio
from fastapi.encoders import jsonable_encoder

from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from Repository import Repository
from tables import Product, Client, Agreement

from start_session import get_session, cli

import logging

logger = logging.getLogger(__name__)

app = FastAPI()

repo = Repository()


def calculate_age(birth_date_str: str) -> int:
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/product", status_code=200, summary="Get all products", response_model=list[schemas.ProductSchema])
async def get_products(pe_session: AsyncSession = Depends(get_session)):
    resp = await repo.select_all(Product, pe_session)
    return resp


@app.post("/product", status_code=200, summary="Set new product")
async def post_product(product: schemas.CreateProduct, pe_session: AsyncSession = Depends(get_session)):
    product_item = json.loads(product.model_dump_json())
    try:
        await repo.post_item(Product, product_item, pe_session)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Продукт уже существует")
    except DBAPIError or DataError:
        raise HTTPException(status_code=400, detail="Переданы неверные данные о продукте")


@app.get("/client/{passport_number}", status_code=200, summary="Check client by it's passport number",
         response_model=schemas.ClientSchema)
async def get_client_by_passport_number(passport_number: str, pe_session: AsyncSession = Depends(get_session)):
    selected_client = await repo.select_by_criteria(Client, ['client_passport_number'], [passport_number], pe_session)
    if not selected_client:
        return JSONResponse(status_code=404, content={
            "message": "Клиента не существует"})
    return selected_client


async def check_client(client: schemas.CreateClient, pe_session: AsyncSession = Depends(get_session)):
    """ Check client by it's data """
    client_item = json.loads(client.model_dump_json())

    client_name = ' '.join([client_item['first_name'], client_item['second_name'], client_item['third_name']])

    client_age = calculate_age(client_item['birthday'])

    names = ['client_name', 'client_age', 'client_phone_number', 'client_passport_number', 'client_salary']
    values = [client_name, client_age, client_item['phone'], client_item['passport_number'], client_item['salary']]

    selected_client = await repo.select_by_criteria(Client, names, values, pe_session)
    return selected_client


@app.post("/client", status_code=200, summary="Add new client")
async def post_client(client: schemas.CreateClient, pe_session: AsyncSession = Depends(get_session)):
    client_item = json.loads(client.model_dump_json())
    client_name = ' '.join([client_item['first_name'], client_item['second_name'], client_item['third_name']])

    client_age = calculate_age(client_item['birthday'])

    try:
        client_id = await repo.post_item(Client, {'client_name': client_name,
                                                  'client_age': client_age,
                                                  'client_phone_number': client_item['phone'],
                                                  'client_passport_number': client_item['passport_number'],
                                                  'client_salary': client_item['salary']
                                                  }, pe_session)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Клиент уже существует")
    except DBAPIError or DataError:
        raise HTTPException(status_code=400, detail="Переданы неверные данные о клиенте")
    return client_id


@app.post("/agreement", status_code=200, summary="Set agreement by it's client and product",
          response_model=schemas.AgreementSchema)
async def post_agreement(agreement: schemas.CreateAgreement, pe_session: AsyncSession = Depends(get_session)):
    results_json = await check_client(agreement, pe_session)
    print(results_json)

    if not results_json:
        client_id = await post_client(agreement, pe_session)
    else:
        client_id = results_json.id

    response_json = await repo.select_by_criteria(Product, ['code'], [agreement.product_code], pe_session)
    if not response_json:
        return JSONResponse(status_code=400, content={
            "message": "Продукта не существует"})
    product_id = response_json.id

    min_origination = response_json.min_origination
    max_origination = response_json.max_origination

    origination_amount = random.uniform(min_origination, max_origination)
    principal_amount = agreement.disbursment_amount + origination_amount

    min_term = response_json.min_term
    max_term = response_json.max_term

    if not check_between(min_term, max_term, agreement.term):
        return JSONResponse(status_code=400, content={
            "message": f"Срок кредита должен составлять от {min_term} до {max_term} месяцев"})

    if not check_between(min_origination, max_origination, origination_amount):
        return JSONResponse(status_code=400, content={
            "message": f"Размер комиссии должен составлять от {min_origination} до {max_origination} руб"})

    min_interest = response_json.min_interest
    max_interest = response_json.max_interest
    if not check_between(min_interest, max_interest, agreement.interest):
        return JSONResponse(status_code=400, content={
            "message": f"Размер процентной ставки должен составлять от {min_interest} до {max_interest} %"})

    min_principal = response_json.min_principal
    max_principal = response_json.max_principal
    if not check_between(min_principal, max_principal, principal_amount):
        return JSONResponse(status_code=400, content={
            "message": f"Сумма кредита должна составлять от {min_principal} до {max_principal} руб"})
    moscow_tz = pytz.timezone("Europe/Moscow")
    try:
        agreement_id = await repo.post_item(Agreement, {'product_id': product_id,
                                                        'client_id': client_id,
                                                        'term': agreement.term,
                                                        'principal': principal_amount,
                                                        'interest': agreement.interest,
                                                        'origination': origination_amount,
                                                        'activation_time': datetime.now(moscow_tz),
                                                        'status': 'New',
                                                        }, pe_session)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Договор уже существует")
    except DBAPIError or DataError:
        raise HTTPException(status_code=400, detail="Переданы неверные данные о договоре")

    return {"agreement_id": agreement_id}


@app.delete("/product/{product_code}", status_code=204, summary="Delete product by it's code")
async def delete_by_product_name(product_code: str, pe_session: AsyncSession = Depends(get_session)):
    deleted = await repo.delete_item(Product, 'code', product_code, pe_session)
    if deleted == 0:
        return JSONResponse(status_code=400, content={
            "message": "Продукта не существует"})


@app.get("/product/{product_code}", status_code=200, summary="Get product by it's code",
         response_model=schemas.ProductSchema)
async def get_by_product_code(product_code: str, pe_session: AsyncSession = Depends(get_session)):
    selected_product = await repo.select_by_criteria(Product, ['code'], [product_code], pe_session)
    if not selected_product:
        return JSONResponse(status_code=404, content={
            "message": "Продукта не существует"})
    return selected_product


@app.get("/hello/{name}", summary="Say hi")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", reload=true)
    cli()
