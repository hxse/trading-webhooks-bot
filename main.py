from fastapi import FastAPI

import os
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
