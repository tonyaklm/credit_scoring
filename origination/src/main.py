from fastapi import FastAPI
import uvicorn
from start_session import origination_async_session
from jobs.scheduler import orig_scheduler
from routers import application
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    orig_scheduler.start()
    try:
        yield
    finally:
        await origination_async_session.close()
        orig_scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.include_router(application.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
    cli()
