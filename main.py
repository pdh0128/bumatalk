from fastapi import FastAPI
from llm import *
app = FastAPI()
@app.get("/")
async def root():
    return {"message": "반가워"}
@app.get("/branch")
async def say_hello(req):
    res = branch(req)
    return res

