from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from start_session import origination_get_session
import schemas
from tables import Application
from Repository import Repository
import json

MY_IP_ADDRESS = ""

SCORING_URL = f"http://{MY_IP_ADDRESS}:5003"
repo = Repository()


async def update_status(application_id: int, new_status: str):
    """ Изменяет статус заявки по ее id"""

    async for orig_session in origination_get_session():
        await repo.update_item(Application, 'id', application_id, 'status', new_status, orig_session)


async def get_new_applications():
    """ Возвращает все заявки со статусом NEW"""

    async for orig_session in origination_get_session():
        return await repo.select_by_criteria(Application, ['status'], ['new'], orig_session)


async def send_application_to_scoring(application: Application):
    """ Отправляет заявку в Scoring"""
    headers = {"Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        try:
            await client.post(f"{SCORING_URL}/",
                              json=json.dumps(application.as_dict(), indent=4, sort_keys=True, default=str),
                              headers=headers)
        except httpx.ConnectError:
            return False
    return True


async def scan_and_send_applications():
    new_applications = await get_new_applications()

    for application in new_applications:
        if await send_application_to_scoring(application):
            await update_status(application.id, "scoring")


def start_orig_scheduler():
    orig_scheduler = AsyncIOScheduler()
    orig_scheduler.add_job(scan_and_send_applications, 'interval', minutes=1)
    orig_scheduler.start()
