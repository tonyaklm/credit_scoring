from fastapi import Depends
from fastapi import HTTPException
import json
from sqlalchemy.exc import IntegrityError, DataError, DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
import schemas
from common.Repository import repo
from tables import Client
from start_session import pe_get_session
from validation import calculate_age


async def check_client(client: schemas.CreateClient, pe_session: AsyncSession = Depends(pe_get_session)):
    """ Check client by it's data """
    client_item = json.loads(client.model_dump_json())

    client_name = ' '.join([client_item['first_name'], client_item['second_name'], client_item['third_name']])

    client_age = calculate_age(client_item['birthday'])

    names = ['client_name', 'client_age', 'client_phone_number', 'client_passport_number', 'client_salary']
    values = [client_name, client_age, client_item['phone'], client_item['passport_number'], client_item['salary']]

    selected_client = await repo.select_by_criteria(Client, names, values, pe_session)
    return selected_client if not selected_client else selected_client[0]


async def post_client(client: schemas.CreateClient, pe_session: AsyncSession = Depends(pe_get_session)):
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
