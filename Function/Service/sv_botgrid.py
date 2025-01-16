
from Function.MongoDatabase import Config
from Function.Models.model_routes_infoPrice import req_getprice,IsUpdate,DeleteRequest
from Function.Models.model_routes_botGrid import oj_Order
import asyncio
import requests
from Function.Models.model_routes_botGrid import req_bot
from datetime import datetime,timedelta
import json
import websocket

db= Config.connet()

    
def fn_insertOrder(req:oj_Order ):
   
    print("insertOrder **********")
    print(req)
    ojData = []
    #for row in data:
    #    # Map row data to a dictionary
    #    oj = {
    #        "timestamp": row[0],  # Open time
    #        "open": row[1],
    #        "high": row[2],
    #        "low": row[3],
    #        "close": row[4],
    #        "volume": row[5],
    #        "Create_Date": current_time,
    #    }
    #    ojData.append(oj)
    #
    ## Check if multiple rows or a single row
    #if len(ojData) == 1:
    #    # Insert a single document
    #    result = db[table_collection].insert_one(ojData[0])
    #else:
    #    # Insert multiple documents
    #    result = db[table_collection].insert_many(ojData)
    #
    #return result
    
def update_order_status(req:oj_Order):
    print("update_order_status **********")
    print(req)