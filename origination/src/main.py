from fastapi import FastAPI
import uvicorn
from start_session import cli
from jobs.scheduler import start_orig_scheduler
from routers import application

app = FastAPI()

app.include_router(application.router)

start_orig_scheduler()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
    cli()
