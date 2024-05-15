from mt5 import MetaTrader5
import datetime
import pandas as pd
import time
import pytz
from tool import freq_dict,round_number,name_dict,create_order,close_order,sltp_order
from loguru import logger

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
    return data.replace("\n","<br>").replace("Long Entry:","<mark>Long Entry:</mark>").replace("Short Entry:","<mark>Short Entry:</mark>")

@logger.catch
def get_data(symbol, freq, count):
    if freq not in freq_dict:
        return None
    
    t = datetime.datetime.now()
    rate = mt.copy_rates_from(symbol, freq_dict[freq](mt), t, count)
    data = pd.DataFrame(rate)
    data["date"] = pd.to_datetime(data["time"], unit="s")
    # data.set_index("date",inplace=True)
    logger.info("get data: symbol={} freq={} count={}", symbol,freq,count)
    return data.to_dict(orient='list')

@logger.catch
def run_trading(data, enable_exit=True):
    deviation=6
    res={}
    name=name_dict[data["ticker"]]["name"] if "!"in data["ticker"] else data["ticker"] 
    if data["message"] =="Long Entry":
        price=mt.symbol_info_tick(name).ask
        logger.info("Long Entry: name={} time={} qty={} price={} sl={} tp={} sl_round={} tp_round={}",name,data["time"],data["size"],price,data["sl"],data["tp"],data["sl_round"],data["tp_round"])
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
    if data["message"]== "Short Entry":
        price=mt.symbol_info_tick(name).bid
        logger.info("Short Entry: name={} time={} qty={} price={} sl={} tp={} sl_round={} tp_round={}",name,data["time"],data["size"],price,data["sl"],data["tp"],data["sl_round"],data["tp_round"])
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
    if data["message"]=="Long Exit" and enable_exit:
        logger.info("Long Exit: name={} time={} qty={} sl_round={} tp_round={}", name,data["time"],data["size"],data["sl_round"],data["tp_round"])
        res=close_order(mt=mt, symbol=name, close_qty=data["size"],deviation=deviation)
    if data["message"]=="Short Exit" and enable_exit:
        logger.info("Short Exit: name={} time={} qty={} sl_round={} tp_round={}", name,data["time"],data["size"],data["sl_round"],data["tp_round"])
        res=close_order(mt=mt, symbol=name, close_qty=data["size"],deviation=deviation)
    if data["message"]=="Clear All":
        logger.info("Clear All: name={} time={}", name, data["time"])
        res=close_order(mt=mt, symbol=name, close_qty="all",deviation=deviation)
    if data["message"]=="Change SLTP":
        logger.info("Change SLTP: name={} time={} sl_round={} tp_round={}", name, data["time"],data["sl_round"],data["tp_round"])
        res=sltp_order(mt=mt, symbol=name, sl=data["sl_round"],tp=data["tp_round"])
    logger.info("res: {}", res)
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

