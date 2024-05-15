from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
import os
from tool import convert
from mt5_trader import run_trading,check_account,check_version,get_data,get_log

try:
    token_env=os.environ['webhooks_token']
except KeyError as e:
    print(e)

app = FastAPI()

@app.get("/")
async def check_version_route(token:str=None):
    # if token!=token_env:
    #     return  {"error": "token is incorrect"}
    return check_version()

@app.get("/account")
async def check_account_route(token:str=None):
    return check_account()

@app.get("/log", response_class=HTMLResponse)
async def get_log_route(token:str=None):
    return get_log().replace("\n","<br>")

@app.get("/data")
async def get_data_route(token:str=None,symbol:str='', freq:str='', count:int=0):
    '''
    /data?symbol=MCLEM24&freq=5m&count=100
    '''
    return get_data(symbol,freq,count)

@app.post("/webhook")
async def webhook(request: Request):
    res= await request.json()
    data= convert(res)
    r= run_trading(data)
    return {}
