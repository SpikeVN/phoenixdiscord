from fastapi import FastAPI
from multiprocessing import Process
import main


app = FastAPI()


@app.get("/")
async def root():
    proc = Process(target=main.main)
    proc.start()
    return {"code": "500", "message": "API not yet available!"}
