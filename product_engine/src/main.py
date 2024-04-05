from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
from fastapi.encoders import jsonable_encoder
from start_session import product_engine_session
from jobs.scheduler import pe_scheduler
from routers import agreements, products
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    pe_scheduler.start()
    try:
        yield
    finally:
        await product_engine_session.close()
        pe_scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.include_router(agreements.router)
app.include_router(products.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
        _: Request,
        exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}", summary="Say hi")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
