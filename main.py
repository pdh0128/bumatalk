from fastapi import FastAPI
from agent import bumatalk
app = FastAPI()
@app.get("/")
async def root():
    return {"message": "반가워"}
@app.get("/bumatalk")
async def say_hello(req):
    res = bumatalk(req)
    return res

