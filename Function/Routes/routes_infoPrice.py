from fastapi import APIRouter,HTTPException
from Function.Models.model_routes_infoPrice import req_getprice,DeleteRequest
from Function.Service.sv_infoPrice import (LoadPrice,load_date,
                                           load_data,
                                           dateTime_To_timestamp,
                                           deleteData,
                                           timeLoadAPI,
                                           Load_bar_lazy,
                                           LoadPrice_Start)

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
        
        return resps
    
@r_infoPrice.post("/infoPrice/getprice_start")
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
        try:
        
            resp= []
            resp = LoadPrice_Start(req)
            print(type(resp))
            resp_converted = convert_objectid(resp)
            resps = JSONResponse(content=resp_converted)
            return resps
        except Exception as e:
            print(f'Error infoPrice/getprice_start getprice : {e}')
@r_infoPrice.post("/infoPrice/Load_bar_lazy")
def Loadbarlazy(req: req_getprice):
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
        resp = Load_bar_lazy(req)
        print(type(resp))
        resp_converted = convert_objectid(resp)
        resps = JSONResponse(content=resp_converted)
        
        return resps
    

@r_infoPrice.get("/infoPrice/date")
def get_ValibleDateData():
    print(" sss")
    resp = load_date('XRPUSDT_1m')
    
    ## resp_converted = convert_objectid(resp)
    ## #
    ## resps = JSONResponse(content=resp_converted)
    return resp


@r_infoPrice.post("/infoPrice/loadPrice")
def get_price(req: req_getprice):
    """ 
            "symbol":"XRPUSDT",
            "tf":"1m",
            "getAll": false,
            "datefrom":"18-12-2024",
            "dateto":"18-12-2025",
            "ohlc":"ohlc"
    """
    print("get_price")
    symbol = req.symbol
    interval = req.tf
    limit =0
    
    datefrom = timeLoadAPI(req.datefrom)
    EndTime= timeLoadAPI(req.dateto)
    resp = load_data(symbol, interval, limit, datefrom,EndTime)
    
    #resp_converted = convert_objectid(resp)
    ## #
    #resps = JSONResponse(content=resp_converted)
    return resp


@r_infoPrice.post("/infoPrice/delete")
def delete_Data(req : DeleteRequest):
    resp = deleteData(req.tableName)
    return resp