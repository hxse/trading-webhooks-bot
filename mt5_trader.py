from mt5 import MetaTrader5
import datetime
import pandas as pd
import time
import pytz
from tool import freq_dict,round_number,name_dict,create_order,close_order,sltp_order

mt = MetaTrader5(host="127.0.0.1", port=8721)
mt.initialize()
print(mt.version())

def check_version():
    return {
        "MetaTrader5 version":mt.version()
    }

def check_account():
    account = mt.account_info()
    return { 
            "balance":account.balance,
            "currency": account.currency,
            "server": account.server, 
            "company":account.company
            }
    
def get_data(symbol, freq, count):
    if freq not in freq_dict:
        return None
    
    t = datetime.datetime.now()
    rate = mt.copy_rates_from(symbol, freq_dict[freq](mt), t, count)
    data = pd.DataFrame(rate)
    data["date"] = pd.to_datetime(data["time"], unit="s")
    # data.set_index("date",inplace=True)
    return data.to_dict(orient='list')

def run_trading(data, enable_exit=True):
    deviation=6
    res={}
    name=name_dict[data["ticker"]]["name"] if "!"in data["ticker"] else data["ticker"] 
    if data["message"] =="Long Entry":
        res=create_order(
                     mt=mt,
                     symbol=name,
                     qty=data["size"], 
                     order_type=mt.ORDER_TYPE_BUY ,
                     price=mt.symbol_info_tick(name).ask,
                     sl=data["sl_round"],
                     tp=data["tp_round"],
                     deviation=deviation
                     )
    if data["message"]== "Short Entry":
        res=create_order(
                     mt=mt,
                     symbol=name,
                     qty=data["size"], 
                     order_type=mt.ORDER_TYPE_SELL ,
                     price=mt.symbol_info_tick(name).bid,
                     sl=data["sl_round"],
                     tp=data["tp_round"],
                     deviation=deviation
                     )
    if data["message"]=="Long Exit" and enable_exit:
        res=close_order(mt=mt, symbol=name, close_qty=data["size"],deviation=deviation)
    if data["message"]=="Short Exit" and enable_exit:
        res=close_order(mt=mt, symbol=name, close_qty=data["size"],deviation=deviation)
    if data["message"]=="Clear All":
        res=close_order(mt=mt, symbol=name, close_qty="all",deviation=deviation)
    if data["message"]=="Change SLTP":
        res=sltp_order(mt=mt, symbol=name, sl=data["sl_round"],tp=data["tp_round"])
    print(res)
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

