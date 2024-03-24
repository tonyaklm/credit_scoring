from fastapi import FastAPI
import uvicorn

from routers import origination, product_engine

app = FastAPI()

app.include_router(origination.router)
app.include_router(product_engine.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
