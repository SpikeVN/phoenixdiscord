from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"code": "500", "message": "API not yet available!"}
