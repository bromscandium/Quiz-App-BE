import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def health_chec():
    return {"status_code": 200, "detail": "ok", "result": "working"}


def start():
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
