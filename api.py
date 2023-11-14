from fastapi import FastAPI
from multiprocessing import Process
import main


app = FastAPI()


@app.get("/")
async def root():
    return {"code": "500", "message": "API not yet available!"}


proc = Process(
    target=main.main,
    daemon=True,
)
proc.start()
