from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import json
from sqlalchemy.exc import IntegrityError, DataError, DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
import schemas
from common.Repository import repo
from tables import Product
from start_session import pe_get_session

router = APIRouter()


@router.get("/product", status_code=200, summary="Get all products", response_model=list[schemas.ProductSchema],
            tags=["products"])
async def get_products(pe_session: AsyncSession = Depends(pe_get_session)):
    resp = await repo.select_all(Product, pe_session)
    return resp


@router.post("/product", status_code=200, summary="Set new product", tags=["products"])
async def post_product(product: schemas.CreateProduct, pe_session: AsyncSession = Depends(pe_get_session)):
    product_item = json.loads(product.model_dump_json())
    try:
        await repo.post_item(Product, product_item, pe_session)
    except IntegrityError:
        raise HTTPException(status_code=409, detail=f"Продукт с кодом {product.code} уже существует")
    except DBAPIError or DataError:
        raise HTTPException(status_code=400, detail="Переданы неверные данные о продукте")


@router.delete("/product/{product_code}", status_code=204, summary="Delete product by it's code", tags=["products"])
async def delete_by_product_name(product_code: str, pe_session: AsyncSession = Depends(pe_get_session)):
    deleted = await repo.delete_item(Product, 'code', product_code, pe_session)
    if deleted == 0:
        return JSONResponse(status_code=400, content={
            "message": f"Продукта с кодом {product_code} не существует"})


@router.get("/product/{product_code}", status_code=200, summary="Get product by it's code",
            response_model=schemas.ProductSchema, tags=["products"])
async def get_by_product_code(product_code: str, pe_session: AsyncSession = Depends(pe_get_session)):
    selected_product = await repo.select_by_criteria(Product, ['code'], [product_code], pe_session)
    if not selected_product:
        return JSONResponse(status_code=404, content={
            "message": f"Продукта с кодом {product_code} не существует"})
    return selected_product[0]
