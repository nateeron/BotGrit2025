
from Function.MongoDatabase import Config 
from Function.Models.model_routes_infoPrice import req_getprice,IsUpdate,DeleteRequest
from Function.Models.model_routes_botGrid import oj_Order
import asyncio
import requests
from Function.Models.model_routes_botGrid import req_bot,infoPrice,check_price,backtest,GetinfoBacktest
from datetime import datetime,timedelta
import json
import Function.Service.BotGrit_CheckPrice_Fast_API_FN_buy1_3 as FN_buy
from bson import ObjectId
from fastapi.responses import JSONResponse
import time

db= Config.connet()
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
    try:
        table_collection = "XRPUSDT_1m"
        start_time = time.time()
        data = None
        #data = list(db[table_collection].find().sort("timestamp", 1).limit(10))  
        if req.limit == 0:
            data = list(db[table_collection].find().sort("timestamp", -1))   
        else:
            data = list(db[table_collection].find().sort("timestamp", -1).limit(req.limit))   
        end_time = time.time()
        elapsed_time = end_time - start_time
        start_time = end_time
        print(f" 1 Process took {elapsed_time:.4f} seconds")
    
        symbo = req.symbol
        nameTime = datetime.now().strftime('%Y_%m_%d_%H.%M.%S')
    
        data.reverse()
    
        table_collections = "OrderBuy"#+nameTime
        # Clear Data
        db[table_collections].delete_many({})
        end_time = time.time()
        elapsed_time = end_time - start_time
        start_time = end_time
        print(f" 2 Process took {elapsed_time:.4f} seconds")
        order_manager = FN_buy.OrderManager()  # Create an instance of OrderManager
        print("len >> ",len(data))
        resp = order_manager.check_price_buy(data)
        #print("sv_botgrid_Backtest.py :",resp)
            #print("Success ........ok")
        # datas = list(db[table_collections].find().sort("timestamp", -1))    
        # resp_converted = convert_objectid(datas)
        # resps = JSONResponse(content=resp_converted)
        return []
    except Exception as e:
        print("Error Function\Service\sv_botgrid_Backtest1_3.py -def Backtest_start() :",e)
        return JSONResponse(content={"error": str(e)})


def data_Backtest(req:GetinfoBacktest):
    print(req)
    table_collections = "OrderBuy"
    #datas = list(db[table_collections].find({"timestem_buy":{"$lte":req.DateFrom}}).sort("timestem_buy",1))    
    datas = list(db[table_collections].find().sort("timestem_buy",1))    
    resp_converted = convert_objectid(datas)
    resps = JSONResponse(content=resp_converted)
    return resps