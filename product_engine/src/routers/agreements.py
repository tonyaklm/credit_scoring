from fastapi import APIRouter
import random
from fastapi import Depends
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import json
from sqlalchemy.exc import IntegrityError, DataError, DBAPIError
import pytz
from sqlalchemy.ext.asyncio import AsyncSession
import schemas
from datetime import datetime
from common.Repository import repo
from tables import Product, Agreement
from start_session import pe_get_session
from validation import check_between
from routers.clients import check_client, post_client

router = APIRouter()


@router.post("/agreement", status_code=200, summary="Set agreement by it's client and product",
             response_model=schemas.AgreementSchema, tags=["agreements"])
async def post_agreement(agreement: schemas.CreateAgreement, pe_session: AsyncSession = Depends(pe_get_session)):
    results_json = await check_client(agreement, pe_session)

    if not results_json:
        client_id = await post_client(agreement, pe_session)
    else:
        client_id = results_json.id
    product_code = agreement.product_code

    response_json = await repo.select_by_criteria(Product, ['code'], [product_code], pe_session)
    if not response_json:
        return JSONResponse(status_code=400, content={
            "message": f"Продукта с кодом {product_code} не существует"})
    selected_product = response_json[0]

    min_origination = selected_product.min_origination
    max_origination = selected_product.max_origination

    origination_amount = random.uniform(min_origination, max_origination)
    principal_amount = agreement.disbursment_amount + origination_amount

    min_term = selected_product.min_term
    max_term = selected_product.max_term

    if not check_between(min_term, max_term, agreement.term):
        return JSONResponse(status_code=400, content={
            "message": f"Срок кредита должен составлять от {min_term} до {max_term} месяцев"})

    if not check_between(min_origination, max_origination, origination_amount):
        return JSONResponse(status_code=400, content={
            "message": f"Размер комиссии должен составлять от {min_origination} до {max_origination} руб"})

    min_interest = selected_product.min_interest
    max_interest = selected_product.max_interest
    if not check_between(min_interest, max_interest, agreement.interest):
        return JSONResponse(status_code=400, content={
            "message": f"Размер процентной ставки должен составлять от {min_interest} до {max_interest} %"})

    min_principal = selected_product.min_principal
    max_principal = selected_product.max_principal
    if not check_between(min_principal, max_principal, principal_amount):
        return JSONResponse(status_code=400, content={
            "message": f"Сумма кредита должна составлять от {min_principal} до {max_principal} руб"})
    moscow_tz = pytz.timezone("Europe/Moscow")
    try:
        agreement_id = await repo.post_item(Agreement, {'product_code': product_code,
                                                        'client_id': client_id,
                                                        'term': agreement.term,
                                                        'principal': principal_amount,
                                                        'interest': agreement.interest,
                                                        'origination': origination_amount,
                                                        'activation_time': datetime.now(moscow_tz),
                                                        'status': 'new',
                                                        }, pe_session)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Договор уже существует")
    except DBAPIError or DataError:
        raise HTTPException(status_code=400, detail="Переданы неверные данные о договоре")

    return {"agreement_id": agreement_id}
