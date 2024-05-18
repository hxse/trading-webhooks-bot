from mt5 import MetaTrader5
import datetime
import pandas as pd
import time
import os
import pytz
from tool import freq_dict,round_number,name_dict,create_order,close_order,sltp_order,convert_history_deals,count_history_deals,req_tg_bot
from loguru import logger

try:
    tg_bot_url_api=os.environ["tg_bot_url_api"]
except KeyError as e:
    tg_bot_url_api=None


log_path="trader.log"
logger.add(log_path, rotation="50 MB",  format="{time:YYYY-MM-DD HH:mm:ss!UTC} | {level} | {message}", backtrace=True, diagnose=True)


mt = MetaTrader5(host="127.0.0.1", port=8721)
mt.initialize()
logger.info("init mt5 version: {}", mt.version())


@logger.catch
def check_version():
    version = mt.version()
    logger.info("get mt5 version: {}", version)
    return {
        "MetaTrader5 version":version
    }

@logger.catch
def check_account():
    account = mt.account_info()
    logger.info("get account: balance={} currency={} server={} company={}", account.balance,account.currency,account.server,account.company)
    return { 
            "balance":account.balance,
            "currency": account.currency,
            "server": account.server, 
            "company":account.company
            }

@logger.catch
def get_log():
    with open(log_path, 'r', encoding='utf-8') as file:
         data = file.read()
    return data.replace("\n","<br>").replace("Long Entry:","<mark>Long Entry:</mark>").replace("Short Entry:","<mark>Short Entry:</mark>").replace("Long Exit:",'<mark style="background-color:burlywood;">Long Exit:</mark>').replace("Short Exit:",'<mark style="background-color:burlywood;">Short Exit:</mark>')

@logger.catch
def get_data(symbol, freq, count):
    if freq not in freq_dict:
        return None
    
    t = datetime.datetime.now()
    rate = mt.copy_rates_from(symbol, freq_dict[freq](mt), t, count)
    data = pd.DataFrame(rate)
    data["date"] = pd.to_datetime(data["time"], unit="s")
    # logger.info("get data: symbol={} freq={} count={}", symbol,freq,count)
    return data.to_dict(orient='list')

@logger.catch
def get_history_deals(days=7):
    now=datetime.datetime.now()
    data =mt.history_deals_get(now-datetime.timedelta(days=days), now)
    data=convert_history_deals(list(data))
    countData=count_history_deals(data)
    # logger.info("get deals: days={}", days)
    return [*data,countData]

@logger.catch
def run_trading(data, enable_exit=True):
    deviation=6
    res={}
    name=name_dict[data["ticker"]]["name"] if "!"in data["ticker"] else data["ticker"] 
    if data["message"] =="Long Entry":
        price=mt.symbol_info_tick(name).ask
        res=create_order(
                     mt=mt,
                     symbol=name,
                     qty=data["size"], 
                     order_type=mt.ORDER_TYPE_BUY ,
                     price=price,
                     sl=data["sl_round"],
                     tp=data["tp_round"],
                     deviation=deviation
                     )
        
        message=f'Long Entry: name={name} time={data["time"]} qty={data["size"]} price={price} sl={data["sl"]} tp={data["tp"]} sl_round={data["sl_round"]} tp_round={data["tp_round"]}'
        logger.info(message)
        req_tg_bot(tg_bot_url_api,message=message)

    if data["message"]== "Short Entry":
        price=mt.symbol_info_tick(name).bid
        res=create_order(
                     mt=mt,
                     symbol=name,
                     qty=data["size"], 
                     order_type=mt.ORDER_TYPE_SELL ,
                     price=price,
                     sl=data["sl_round"],
                     tp=data["tp_round"],
                     deviation=deviation
                     )
        
        message=f'Short Entry: name={name} time={data["time"]} qty={data["size"]} price={price} sl={data["sl"]} tp={data["tp"]} sl_round={data["sl_round"]} tp_round={data["tp_round"]}'
        logger.info(message)
        req_tg_bot(tg_bot_url_api,message=message)

    if data["message"]=="Long Exit" and enable_exit:
        res=close_order(mt=mt, symbol=name, close_qty=data["size"],deviation=deviation)
        
        message=f'Long Exit: name={name} time={data["time"]} qty={data["size"]} sl_round={data["sl_round"]} tp_round={data["tp_round"]}'
        logger.info(message)
        req_tg_bot(tg_bot_url_api,message=message)
        
    if data["message"]=="Short Exit" and enable_exit:
        res=close_order(mt=mt, symbol=name, close_qty=data["size"],deviation=deviation)
        
        message=f'Short Exit: name={name} time={data["time"]} qty={data["size"]} sl_round={data["sl_round"]} tp_round={data["tp_round"]}'
        logger.info(message)
        req_tg_bot(tg_bot_url_api,message=message)
        
    if data["message"]=="Clear All":
        res=close_order(mt=mt, symbol=name, close_qty="all",deviation=deviation)
        
        message=f'Clear All: name={name} time={data["time"]}'
        logger.info(message)
        req_tg_bot(tg_bot_url_api,message=message)
        
    if data["message"]=="Change SLTP":
        res=sltp_order(mt=mt, symbol=name, sl=data["sl_round"],tp=data["tp_round"])
        
        message=f'Change SLTP: name={name} time={data["time"]} sl_round={data["sl_round"]} tp_round={data["tp_round"]}'
        logger.info(message)
        # req_tg_bot(tg_bot_url_api,message=message)

    logger.info("res: {}", res)
    logger.info("data: {}", data)
    return res

if __name__ == '__main__':
    tz = pytz.timezone("America/New_York")
    my_order_type=0
    if my_order_type == 0:
        data={'ticker': 'MCL1!', 'action': 'Long', 'size': 2.0, 'price': 78.88, 'sl': 78.88043, 'tp': 79.12957, 'timestamp': 1715668980000, 'message': 'Long Entry', 'sl_round': 78.72, 'tp_round': 79.17, 'time': datetime.datetime(2024, 5, 14, 2, 43, tzinfo=tz)}
        # data={'ticker': 'MCL1!', 'action': 'Long', 'size': 1.0, 'price': 78.88, 'sl': 78.88043, 'tp': 79.12957, 'timestamp': 1715668980000, 'message': 'Long Exit', 'sl_round': 78.72, 'tp_round': 79.12, 'time': datetime.datetime(2024, 5, 14, 2, 43, tzinfo=tz)}
        data["sl_round"]= data["sl_round"] + 0.1
        data["tp_round"]= data["tp_round"] - 0.1
        data["message"]= "Change SLTP"
        d=run_trading(data)
    else:
        sl = sell_sl_round + 2
        tp = sell_tp_round - 4

