from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import JSONResponse
from config import settings
import json
import httpx
import schemas

router = APIRouter()


@router.post("/application", status_code=200, summary="Redirecting a request set new application to Origination",
             response_model=schemas.ApplicationSchema, tags=["origination"])
async def post_application(request: Request):
    item = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.origination_url}/application", json=item)
        return JSONResponse(status_code=response.status_code, content=response.json())


@router.post("/application/{application_id}/close", status_code=200,
             summary="Redirecting a request close application to Origination", tags=["origination"])
async def close_application(application_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.origination_url}/application/{application_id}/close")
        return JSONResponse(status_code=response.status_code, content=response.json())
