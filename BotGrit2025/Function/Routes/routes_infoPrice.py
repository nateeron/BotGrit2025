from fastapi import APIRouter,HTTPException
from Function.Models.model_routes_infoPrice import req_getprice
from Function.Service.sv_infoPrice import LoadPrice
import json
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
            "datefrom":"10-02-2025",
            "dateto":"10-03-2025",
            "ohcl":"c"
        }
        """
        resp= []
        resp = LoadPrice(req)
        print(type(resp))
        resp_converted = convert_objectid(resp)
        resps = JSONResponse(content=resp_converted)
        print(resps)
        
        return resps
