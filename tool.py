import datetime
import pytz

name_dict = {
    "MCL1!": {"zone":"America/New_York","trade_tick_size":0.01},
    "MGC1!": {"zone":"America/New_York","trade_tick_size":0.1},
    "MHG1!": {"zone":"America/New_York","trade_tick_size":0.0005},
    "MES1!": {"zone":"America/Chicago","trade_tick_size":0.25},
    "MNQ1!": {"zone":"America/Chicago","trade_tick_size":0.25},
    "MYM1!": {"zone":"America/Chicago","trade_tick_size":1},
    "M2K1!": {"zone":"America/Chicago","trade_tick_size":0.1},
    "M6A1!": {"zone":"America/Chicago","trade_tick_size":0.0001},
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
