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
import uvicorn
import typer
import pytz
import httpx
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

app = FastAPI()

MY_IP_ADDRESS = ""  # мой внешний адрес вашего ПК

PE_URL = f"http://{MY_IP_ADDRESS}:5001"
ORIGINATION_URL = f"http://{MY_IP_ADDRESS}:5002"


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


class AgreementSchema(BaseModel):
    agreement_id: int


class ApplicationSchema(BaseModel):
    application_id: int


cli = typer.Typer()


@cli.command()
def db_init_models():
    asyncio.run(init_models())
    print("Done")


@app.get("/product", status_code=200, summary="Get all products", response_model=list[ProductSchema])
async def get_products():
    logging.info('I got your request')
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PE_URL}/product")
        return JSONResponse(status_code=response.status_code, content=response.json())


@app.get("/product/{product_code}", status_code=200, summary="Get product by it's code", response_model=ProductSchema)
async def get_by_product_code(product_code):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PE_URL}/product/{product_code}")
        return JSONResponse(status_code=response.status_code, content=response.json())


@app.post("/agreement", status_code=200, summary="Set agreement by it's client and product",
          response_model=AgreementSchema)
async def post_agreement(request: Request):
    item = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{PE_URL}/agreement", json=item)
        return JSONResponse(status_code=response.status_code, content=response.json())


@app.post("/application", status_code=200, summary="Set new application", response_model=ApplicationSchema)
async def post_application(request: Request):
    item = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{ORIGINATION_URL}/application", json=item)
        return JSONResponse(status_code=response.status_code, content=response.json())


@app.post("/application/{application_id}/close", status_code=200, summary="Close application by its id")
async def close_application(application_id):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{ORIGINATION_URL}/application/{application_id}/close")
        return JSONResponse(status_code=response.status_code, content=response.json())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", reload=true)
    cli()
