from fastapi import Depends
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
from datetime import datetime
import httpx
import pytz

from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from Repository import Repository
from tables import Application

from start_session import origination_get_session, cli

app = FastAPI()

repo = Repository()
MY_IP_ADDRESS = ""

PE_URL = f"http://{MY_IP_ADDRESS}:5001"


@app.post("/application", status_code=200, summary="Set new application", response_model=schemas.ApplicationSchema)
async def post_application(application: schemas.CreateApplication,
                           orig_session: AsyncSession = Depends(origination_get_session)):
    headers = {"Content-Type": "application/json"}
    application_item = json.loads(application.model_dump_json())

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{PE_URL}/client/{application.passport_number}")
        except httpx.ConnectError:
            return JSONResponse(status_code=503, content={"Не удалось подключится к PE"})
        selected_client = response.json()
        client_code = response.status_code

    if client_code != 200:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{PE_URL}/client", json=application_item, headers=headers)
            except httpx.ConnectError:
                return JSONResponse(status_code=503, content={"Не удалось подключится к PE"})

            new_client_id = response.json()
            if response.status_code == 200:
                client_id = new_client_id
            else:
                return JSONResponse(status_code=response.status_code, content=response.json())
    else:
        client_id = selected_client['id']

    product_code = application_item['product_code']

    application_names = ['client_id', 'product_code']
    application_values = [client_id, product_code]

    results_json = await repo.select_by_criteria(Application, application_names, application_values, orig_session)

    moscow_tz = pytz.timezone("Europe/Moscow")
    time_of_application = datetime.now(moscow_tz)

    new_item = {'client_id': client_id,
                'product_code': product_code,
                'time_of_application': time_of_application,
                'disbursment_amount': application_item['disbursment_amount'],
                'status': 'new'
                }
    if results_json and (results_json.disbursment_amount == application_item['disbursment_amount'] or (
            results_json.time_of_application - time_of_application).days < 7):
        # совпадение по полям или меньше 7 дней с прошлой заявки на этот же продукт
        application_id = results_json.id

        await repo.update_item(Application, 'id', application_id, 'status', 'closed', orig_session)
        return JSONResponse(status_code=409, content={"application_id": application_id,
                                                      "message": "Заявка уже существует"})
    else:
        application_id = await repo.post_item(Application, new_item, orig_session)

    return {"application_id": application_id}


@app.post("/application/{application_id}/close", status_code=200, summary="Close application by its id")
async def close_application(application_id: int, orig_session: AsyncSession = Depends(origination_get_session)):
    application = await repo.select_by_criteria(Application, ['id'], [application_id], orig_session)
    if not application:
        return JSONResponse(status_code=404, content={
            "message": f"Заявки {application_id} не существует"})

    await repo.update_item(Application, 'id', application_id, 'status', 'closed', orig_session)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", reload=true)
    cli()
