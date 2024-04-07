from fastapi import FastAPI
import uvicorn
import asyncio
from start_session import origination_async_session
from jobs.scheduler import orig_scheduler
from routers import application
from consumer import consumer
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    orig_scheduler.start()
    asyncio.create_task(consumer.consume())
    try:
        yield
    finally:
        await origination_async_session.close()
        orig_scheduler.shutdown()
        await consumer.stop_consumer()


app = FastAPI(lifespan=lifespan)

app.include_router(application.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
