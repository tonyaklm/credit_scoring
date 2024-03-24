from fastapi import Depends
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import json
from datetime import datetime
import httpx
import pytz
from sqlalchemy.ext.asyncio import AsyncSession
import schemas
from common.Repository import repo
from tables import Application
from config import settings
from start_session import origination_get_session

router = APIRouter()


@router.post("/application", status_code=200, summary="Set new application", response_model=schemas.ApplicationSchema,
             tags=["application"])
async def post_application(application: schemas.CreateApplication,
                           orig_session: AsyncSession = Depends(origination_get_session)):
    application_names = ['product_code']
    application_values = [application.product_code]

    results_json = await repo.select_by_criteria(Application, application_names, application_values, orig_session)

    moscow_tz = pytz.timezone("Europe/Moscow")
    time_of_application = datetime.now(moscow_tz)

    if results_json and (results_json[0].time_of_application - time_of_application).days < 7:
        # совпадение по полям или меньше 7 дней с прошлой заявки на этот же продукт
        application_id = results_json[0].id

        await repo.update_item(Application, 'id', application_id, 'status', 'closed', orig_session)
        return JSONResponse(status_code=409, content={"application_id": application_id,
                                                      "message": "Заявка уже существует"})

    headers = {"Content-Type": "application/json"}
    application_item = json.loads(application.model_dump_json())

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{settings.product_engine_url}/agreement", json=application_item,
                                         headers=headers)
        except httpx.ConnectError:
            return JSONResponse(status_code=503, content={"Не удалось подключится к PE"})
        if response.status_code == 200:
            agreement_id = response.json()['agreement_id']
        else:
            return JSONResponse(status_code=response.status_code, content=response.json())

    new_item = {'agreement_id': agreement_id,
                'product_code': application.product_code,
                'time_of_application': time_of_application,
                'status': 'new'
                }
    application_id = await repo.post_item(Application, new_item, orig_session)

    return {"application_id": application_id}


@router.post("/application/{application_id}/close", status_code=200, summary="Close application by its id",
             tags=["application"])
async def close_application(application_id: int, orig_session: AsyncSession = Depends(origination_get_session)):
    """Закрывает заявку по ее id"""
    application = await repo.select_by_criteria(Application, ['id'], [application_id], orig_session)
    if not application:
        return JSONResponse(status_code=404, content={
            "message": f"Заявки {application_id} не существует"})

    await repo.update_item(Application, 'id', application_id, 'status', 'closed', orig_session)


@router.get("/application/{agreement_id}", status_code=200, summary="Get applications by agreement",
            response_model=list[schemas.BaseApplication], tags=["application"])
async def get_applications(agreement_id: int, orig_session: AsyncSession = Depends(origination_get_session)):
    applications = await repo.select_by_criteria(Application, ['agreement_id'], [agreement_id], orig_session)
    if not applications:
        return JSONResponse(status_code=404, content={
            "message": f"Заявки с кредитным договором {agreement_id} не существует"})
    return applications


@router.post("/application/by/agreement", status_code=200, summary="Set new application",
             response_model=schemas.ApplicationSchema, tags=["application"])
async def post_application_by_agreement(agreement_data: schemas.FinishApplication,
                                        orig_session: AsyncSession = Depends(origination_get_session)):
    moscow_tz = pytz.timezone("Europe/Moscow")
    time_of_application = datetime.now(moscow_tz)

    application_item = json.loads(agreement_data.model_dump_json())
    new_item = {'agreement_id': application_item["agreement_id"],
                'product_code': application_item["product_code"],
                'time_of_application': time_of_application,
                'status': 'new'
                }

    application_id = await repo.post_item(Application, new_item, orig_session)

    return {"application_id": application_id}
