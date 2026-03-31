from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
async def root() -> JSONResponse:
    return JSONResponse(
        content={
            "msg": "Hello Catiy ML",
        },
        status_code=200,
    )
