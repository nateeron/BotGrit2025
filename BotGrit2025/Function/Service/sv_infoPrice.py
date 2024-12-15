
from Function.MongoDatabase import db
from Function.Models.model_routes_infoPrice import req_getprice

def LoadPrice(req:req_getprice):
    
    """
    Retrieve documents (rows) from a collection (table).
    """
    print("*******ok Call Function *******")
    print(req)
    print(req.table_name)
    print(req.datefrom)
    # collection_name = ''
    # if query is None:
    #     query = {}
    # return list(db[collection_name].find(query))
    return []