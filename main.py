from fastapi import FastAPI,Request
import os
from tool import convert

try:
    token_env=os.environ['webhooks_token']
except KeyError as e:
    print(e)

app = FastAPI()

@app.get("/")
async def root(token:str=None):
    if token!=token_env:
        return  {"error": "token is incorrect"}
    print(token,token_env)
    return {"message": "Hello World"}

@app.post("/webhook")
async def input_request(request: Request):
    res= await request.json()
    data= convert(res)
    print(data)
    return data
