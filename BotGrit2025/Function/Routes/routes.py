from fastapi import APIRouter, HTTPException
# from typing import List
from Function.MongoDatabase import Config 

from Function.Models.models import PriceData, PriceResponse,reqCollection_Name,req
# from crud import create_price, read_prices, read_price, update_price, delete_price

db= Config.connet()

price_router = APIRouter()
@price_router.get("/")
def okRun():
      return {"message": "OK RUNNING"}

# @price_router.post("/prices", response_model=PriceResponse)
# async def create_price_endpoint(data: PriceData):
#     collection = 'BNBUSDT_1m'
#     result = create_price(collection, data.dict())
#     if not result:
#         raise HTTPException(status_code=500, detail="Failed to create record")
#     return result

# @price_router.get("/prices", response_model=List[PriceResponse])
# async def read_prices_endpoint():
#     return read_prices(collection)

# @price_router.get("/prices/{id}", response_model=PriceResponse)
# async def read_price_endpoint(id: str):
#     result = read_price(collection, id)
#     if not result:
#         raise HTTPException(status_code=404, detail="Record not found")
#     return result

# @price_router.put("/prices/{id}", response_model=PriceResponse)
# async def update_price_endpoint(id: str, data: PriceData):
#     if not update_price(collection, id, data.dict()):
#         raise HTTPException(status_code=404, detail="Record not found")
#     return read_price(collection, id)

# @price_router.delete("/prices/{id}")
# async def delete_price_endpoint(id: str):
#     if not delete_price(collection, id):
#         raise HTTPException(status_code=404, detail="Record not found")
#     return {"message": "Record deleted successfully"}

@price_router.post("/createTable")
async def create_table():
    """
    Create MongoDB collections (tables) for the required structure.
    """
    # Create collections if they do not exist
    for collection_name in ["XRPUSDT_1m", "BNBUSDT_1m", "OrderBuy", "ConfigBot"]:
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
            print(f"Collection {collection_name} created.")