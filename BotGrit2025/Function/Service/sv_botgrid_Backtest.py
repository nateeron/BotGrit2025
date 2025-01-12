
from Function.MongoDatabase import db
from Function.Models.model_routes_infoPrice import req_getprice,IsUpdate,DeleteRequest
from Function.Models.model_routes_botGrid import oj_Order
import asyncio
import requests
from Function.Models.model_routes_botGrid import req_bot,infoPrice,check_price,backtest,GetinfoBacktest
from datetime import datetime,timedelta
import json
# import Function.Service.BotGrit_CheckPrice_Fast_API_FN_buy as FN_buy
import Function.Service.BotGrit_CheckPrice_Fast_API_FN_buy1_3 as FN_buy


from bson import ObjectId
from fastapi.responses import JSONResponse

def convert_timestamp(timestamp:int):
    """convert

    Args:
        timestamp (int): 1734591480000

    Returns:
        str : 19/12/2567 6:58:00
    """
    # Convert milliseconds to seconds
    timestamp_sec = timestamp / 1000
    # Convert to datetime
    date_time = datetime.utcfromtimestamp(timestamp_sec)
    # Format datetime as string
    return date_time.strftime("%Y-%m-%d %H:%M:%S")

def convert_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)  # Convert ObjectId to string
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}  # Recurse for dictionaries
    elif isinstance(obj, list):
        return [convert_objectid(i) for i in obj]  # Recurse for lists
    return obj 
def Backtest_start(req:backtest):
    """ 
    symbol:str
    price:float
    tf:float
    DateFrom:int
    DateTo:int
    """
    table_collection = "XRPUSDT_1m"
    data = None
    #data = list(db[table_collection].find().sort("timestamp", 1).limit(10))  
    if req.limit == 0:
        data = list(db[table_collection].find().sort("timestamp", -1))   
    else:
        data = list(db[table_collection].find().sort("timestamp", -1).limit(req.limit))   
         
    data2 = list(db[table_collection].find().sort("timestamp", -1))    
    # print("Data :",len(data))
    # print(data)
    symbo = req.symbol
    nameTime = datetime.now().strftime('%Y_%m_%d_%H.%M.%S')
    # froms = data[0]
    # DATAtO = data[len(data)-1]
    # print(len(data))
    # print(froms)
    # print(DATAtO)
    # print('--------------------')
    # print(len(data2))
    # print(data2[0])
    # print( data2[len(data2)-1])
    data.reverse()
    #for ind,x in enumerate(data):
    #   time_action = x['timestamp']
    #   time_action = x['timestamp']
    #   s = convert_timestamp(time_action)
    #   p ="{:.4f}".format(float(x['close']))
    #   print(ind+1,s,p)
    table_collections = "OrderBuy"#+nameTime
    # Clear Data
    db[table_collections].delete_many({})
    
    for x in data:
        price = x['close']
        #print(x)
        time_action = x['timestamp']
        order_manager = FN_buy.OrderManager()  # Create an instance of OrderManager
        req = check_price(
                symbol=symbo,
                price=price,
                tf="1m",
                timestamp=time_action
        )
        resp = order_manager.check_price_buy(req)
        
        # print("sv_botgrid_Backtest.py :",resp)
        #print("Success ........ok")
    datas = list(db[table_collections].find().sort("timestamp", -1))    
    resp_converted = convert_objectid(datas)
    resps = JSONResponse(content=resp_converted)
    return resps

def data_Backtest(req:GetinfoBacktest):
    print(req)
    table_collections = "OrderBuy"
    #datas = list(db[table_collections].find({"timestem_buy":{"$lte":req.DateFrom}}).sort("timestem_buy",1))    
    datas = list(db[table_collections].find().sort("timestem_buy",1))    
    resp_converted = convert_objectid(datas)
    resps = JSONResponse(content=resp_converted)
    return resps