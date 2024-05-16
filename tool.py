import datetime
import pytz
import urllib.parse
import requests

freq_dict={
        "1m":lambda mt: mt.TIMEFRAME_M1,
        "3m":lambda mt: mt.TIMEFRAME_M3,
        "5m":lambda mt: mt.TIMEFRAME_M5,
        "15m":lambda mt: mt.TIMEFRAME_M15,
        "30m":lambda mt: mt.TIMEFRAME_M30,
        "1h":lambda mt: mt.TIMEFRAME_H1,
        "6h":lambda mt: mt.TIMEFRAME_H6,
        "12h":lambda mt: mt.TIMEFRAME_H12,
        "1d":lambda mt: mt.TIMEFRAME_D1,
        "1w":lambda mt: mt.TIMEFRAME_W1,
        "1mn":lambda mt: mt.TIMEFRAME_MN1,
    }
 
name_dict = {
    "MCL1!": {"zone":"America/New_York","trade_tick_size":0.01, "name":"MCLEM24"},
    "MGC1!": {"zone":"America/New_York","trade_tick_size":0.1,"name":"MGCM24"},
    "MHG1!": {"zone":"America/New_York","trade_tick_size":0.0005,"name":"MHGN24"},
    "MES1!": {"zone":"America/Chicago","trade_tick_size":0.25,"name":"MESM24"},
    "MNQ1!": {"zone":"America/Chicago","trade_tick_size":0.25,"name":"MNQM24"},
    "MYM1!": {"zone":"America/Chicago","trade_tick_size":1,"name":"MYMM24"},
    "M2K1!": {"zone":"America/Chicago","trade_tick_size":0.1,"name":"M2KM24"},
    "M6A1!": {"zone":"America/Chicago","trade_tick_size":0.0001,"name":"M6AM24"},
}

def round_number(n, trade_tick_size=0.01):
    # 有些品种是0.25一跳, 有些是0.01
    assert trade_tick_size>0, "trade_tick_size can not be zero"   

    if trade_tick_size >= 1:
        return round(n / trade_tick_size) * trade_tick_size
    
    digits = len(str(trade_tick_size).split(".")[1])

    pow_digits = pow(10, digits)
    trade_tick_size = trade_tick_size * pow_digits
    n = round(n, digits)  
    d = round((n - int(n)) * pow_digits, digits) 
    c = round(d / trade_tick_size) * trade_tick_size 
    c = (
        pow_digits if c > pow_digits else c
    )  # fix bug round_number(n=5172.98, trade_tick_size= 0.13) -> 5173.04 -> 5173.0
    return float(int(n) + c / pow_digits)  

def convert_time(timestamp, zone):
    tz = pytz.timezone(zone)
    d = datetime.datetime.fromtimestamp(timestamp/1000 if len(str(timestamp))==13 else timestamp, tz)
    return d

def convert(json):
    if "size"in json:
        json["size"]=float(json["size"])
    if "price"in json:
        json["price"]=float(json["price"])
    if "sl" in json:
        json["sl"]=float(json["sl"])
        json["sl_round"]=round_number(json["sl"],name_dict[json["ticker"]]["trade_tick_size"])
    if "tp" in json:
        json["tp"]=float(json["tp"])
        json["tp_round"]=round_number(json["tp"],name_dict[json["ticker"]]["trade_tick_size"])
    if "timestamp" in json:
        json["timestamp"]=int(json["timestamp"])
        json["time"]= convert_time(json["timestamp"],name_dict[json["ticker"]]["zone"])
    return json

def convert_history_deals(data):
    return [{ "ticket":i.ticket,"order":i.order,"time":i.time,"type":i.type,"entry":i.entry, "magic":i.magic, "position_id":i.position_id, "reason":i.reason, "volume":i.volume, "price":i.price, "commission":i.commission,"swap":i.swap,"profit":i.profit, "fee":i.fee, "symbol":i.symbol,"comment":i.comment, "external_id":i.external_id } for i in data]

def create_order(mt,symbol, qty, order_type, price, sl, tp, deviation):
    request = {
        "action": mt.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(qty),
        "type": order_type,
        "price": price,
        "sl": float(sl),
        "tp": float(tp),
        "deviation": deviation,
        "type_time": mt.ORDER_TIME_GTC,
        "type_filling": mt.ORDER_FILLING_IOC,
    }
    order = mt.order_send(request)
    return order

def _close_order(mt,symbol, position, qty, order_type, price, deviation):
    request = {
        "action": mt.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(qty),
        "type": order_type,
        "position": position,
        "price": price,
        "deviation": deviation,
        "type_time": mt.ORDER_TIME_GTC,
        "type_filling": mt.ORDER_FILLING_IOC,
    }
    order = mt.order_send(request)
    return order


def close_order(mt,symbol, close_qty=1, deviation=5):

    buy_price = mt.symbol_info_tick(symbol).ask
    sell_price = mt.symbol_info_tick(symbol).bid

    p_list = [i for i in mt.positions_get() if i.symbol == symbol]
    if len(p_list) > 0:
        p = p_list[0]
        res = _close_order(
            mt=mt,
            symbol=symbol,
            position=p.ticket,
            qty=p.volume if close_qty == "all" or float(close_qty)>p.volume else float(close_qty),
            order_type=mt.ORDER_TYPE_SELL if p.type ==  mt.ORDER_TYPE_BUY else mt.ORDER_TYPE_BUY,
            price=sell_price if p.type == 0 else buy_price,
            deviation=deviation
        )

def _sltp_order(mt,symbol, position, sl, tp):
    request = {
        "action": mt.TRADE_ACTION_SLTP,
        "symbol": symbol,
        "position": position,
        "sl": float(sl),
        "tp": float(tp),
        "type_time": mt.ORDER_TIME_GTC,
        "type_filling": mt.ORDER_FILLING_IOC,
    }
    return mt.order_send(request)

def sltp_order(mt,symbol, sl, tp):
    p_list = [i for i in mt.positions_get() if i.symbol == symbol]
    if len(p_list) > 0:
        p = p_list[0]
        res = _sltp_order(mt,symbol, p.ticket, sl, tp)
        return res

def req_tg_bot(tg_bot_url_api, message):
    if tg_bot_url_api:
        url=tg_bot_url_api+urllib.parse.quote(message,safe="")
        print(url)
        requests.get(url)

if __name__ == '__main__':
    data = {'ticker': 'MCL1!', 'sl': 78.21909, 'tp': 78.14091, 'timestamp': 1715583600000, 'message': 'Short Alert'}
    timestamp = 1715580000000
    time = convert_time(data["timestamp"], name_dict[data["ticker"]]["zone"])
    print(time)
    print(round_number(78.13634, 0.02)) #78.14
    print(round_number(62.63234, 25)) #75
    print(round_number(5172.6259,0.25)) #5172.75
    print(round_number(78.95634,0.2)) #79.0
    print(round_number(5172.98,0.13))
