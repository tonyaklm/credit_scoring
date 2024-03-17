from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
import json
import asyncio
import uvicorn
import typer
import httpx
import logging

import schemas

app = FastAPI()

MY_IP_ADDRESS = ""  # мой внешний адрес ПК

PE_URL = f"http://{MY_IP_ADDRESS}:5001"
ORIGINATION_URL = f"http://{MY_IP_ADDRESS}:5002"

cli = typer.Typer()


@cli.command()
def db_init_models():
    asyncio.run(init_models())
    print("Done")


@app.get("/product", status_code=200, summary="Redirecting a request get all products to PE",
         response_model=list[schemas.ProductSchema])
async def get_products():
    logging.info('I got your request')
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PE_URL}/product")
        return JSONResponse(status_code=response.status_code, content=response.json())


@app.get("/product/{product_code}", status_code=200, summary="Redirecting a request get product by it's code to PE",
         response_model=schemas.ProductSchema)
async def get_by_product_code(product_code: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PE_URL}/product/{product_code}")
        return JSONResponse(status_code=response.status_code, content=response.json())


@app.post("/agreement", status_code=200, summary="Redirecting a request set agreement to PE",
          response_model=schemas.AgreementSchema)
async def post_agreement(request: Request):
    item = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{PE_URL}/agreement", json=item)
        return JSONResponse(status_code=response.status_code, content=response.json())


@app.post("/application", status_code=200, summary="Redirecting a request set new application to Origination",
          response_model=schemas.ApplicationSchema)
async def post_application(request: Request):
    item = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{ORIGINATION_URL}/application", json=item)
        return JSONResponse(status_code=response.status_code, content=response.json())


@app.post("/application/{application_id}/close", status_code=200,
          summary="Redirecting a request close application to Origination")
async def close_application(application_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{ORIGINATION_URL}/application/{application_id}/close")
        return JSONResponse(status_code=response.status_code, content=response.json())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", reload=true)
    cli()
