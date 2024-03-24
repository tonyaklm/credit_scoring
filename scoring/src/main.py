from fastapi import Request, FastAPI
import uvicorn

app = FastAPI()


@app.post("/", status_code=200)
async def root(request: Request):
    return


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
