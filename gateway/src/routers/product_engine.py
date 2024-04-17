from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import JSONResponse
import json
from config import settings
import httpx
import schemas


router = APIRouter()


@router.get("/product", status_code=200, summary="Redirecting a request get all products to PE",
            response_model=list[schemas.ProductSchema], tags=["product engine"])
async def get_products():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.product_engine_url}/product")
        return JSONResponse(status_code=response.status_code, content=response.json())


@router.get("/product/{product_code}", status_code=200, summary="Redirecting a request get product by it's code to PE",
            response_model=schemas.ProductSchema, tags=["product engine"])
async def get_by_product_code(product_code: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.product_engine_url}/product/{product_code}")
        return JSONResponse(status_code=response.status_code, content=response.json())


@router.post("/agreement", status_code=200, summary="Redirecting a request set agreement to PE",
             response_model=schemas.AgreementSchema, tags=["product engine"])
async def post_agreement(request: Request):
    item = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.product_engine_url}/agreement", json=item)
        return JSONResponse(status_code=response.status_code, content=response.json())

