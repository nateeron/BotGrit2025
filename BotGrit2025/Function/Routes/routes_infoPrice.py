from fastapi import APIRouter,HTTPException
from Function.Models.model_routes_infoPrice import req_getprice
from Function.Service.sv_infoPrice import LoadPrice,load_date,getprice_Api,load_data,dateTime_To_timestamp
import json
from datetime import datetime,timedelta
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from bson import ObjectId
r_infoPrice = APIRouter()
@r_infoPrice.get("/infoPrice/run")
def run():
        return {"message": "OK RUNNING info Price"}


def convert_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)  # Convert ObjectId to string
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}  # Recurse for dictionaries
    elif isinstance(obj, list):
        return [convert_objectid(i) for i in obj]  # Recurse for lists
    return obj 

@r_infoPrice.post("/infoPrice/getprice")
def getprice(req: req_getprice):
        """
        Model send Post on Postman
        {
            "symbol":"XRPUSDT",
            "tf":"1m",
            "getAll": false,
            "datefrom":"18-12-2024",
            "dateto":"18-12-2025",
            "ohlc":"ohlc"
        }
        """
        resp= []
        resp = LoadPrice(req)
        print(type(resp))
        resp_converted = convert_objectid(resp)
        resps = JSONResponse(content=resp_converted)
        print(resps)
        
        return resps
@r_infoPrice.get("/infoPrice/date")
def get_ValibleDateData():
    print(" sss")
    resp = load_date('XRPUSDT_1m')
    
    print(resp)
    ## resp_converted = convert_objectid(resp)
    ## #
    ## resps = JSONResponse(content=resp_converted)
    return resp


@r_infoPrice.get("/infoPrice/getprice")
def get_price():
    print(" get_price")
    symbol = 'XRPUSDT'
    interval = '1m'
    limit ='2'
    
    current_time = dateTime_To_timestamp(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) - 1*60*60
    resp = load_data(symbol, interval, limit, current_time)
    
    print(resp)
    #resp_converted = convert_objectid(resp)
    ## #
    #resps = JSONResponse(content=resp_converted)
    return resp