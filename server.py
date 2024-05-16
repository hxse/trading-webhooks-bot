from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
import os
from tool import convert
from mt5_trader import run_trading,check_account,check_version,get_data,get_log,get_history_deals
from asyncio import run

# try:
#     token_env=os.environ['webhooks_token']
# except KeyError as e:
#     print(e)

# how to use fastapi without block
# https://fastapi.tiangolo.com/async
# https://stackoverflow.com/questions/71516140/fastapi-runs-api-calls-in-serial-instead-of-parallel-fashion

app = FastAPI()

@app.get("/")
def check_version_route(token:str=None):
    # if token!=token_env:
    #     return  {"error": "token is incorrect"}
    return check_version()

@app.get("/account")
def check_account_route(token:str=None):
    return check_account()

@app.get("/log", response_class=HTMLResponse)
def get_log_route(token:str=None):
    return get_log()

@app.get("/deals")
def get_history_deals_route(token:str=None,days:int=7):
    '''
    too slow, should be used with carefully
    '''
    return get_history_deals(days=days)

@app.get("/data")
def get_data_route(token:str=None,symbol:str='', freq:str='', count:int=0):
    '''
    /data?symbol=MCLEM24&freq=5m&count=100
    '''
    return get_data(symbol,freq,count)

@app.post("/webhook")
def webhook_route(request: Request):
    res=run(request.json())
    data= convert(res)
    r= run_trading(data)
    return {}
