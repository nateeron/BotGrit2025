from fastapi import APIRouter
from Function.Models.model_routes_infoPrice import req_getprice
from Function.Service.sv_infoPrice import LoadPrice

r_infoPrice = APIRouter()
@r_infoPrice.get("/infoPrice/run")
def run():
        return {"message": "OK RUNNING info Price"}


@r_infoPrice.post("/infoPrice/getprice")
def getprice(req: req_getprice):
        """Model send Post on Postman
        {

            "table_name":"XRPUSDT_F1",
            "getAll": false,
            "datefrom":"10-02-2025",
            "dateto":"10-03-2025",
            "ohcl":"c"
        }
        
        """
        
        print(req)
        print(req.table_name)
        print(req.getAll)
        print(req.datefrom)
        print(req.dateto)
        print(req.ohcl)
        LoadPrice(req)
        return {"message": "OK RUNNING info Price"}