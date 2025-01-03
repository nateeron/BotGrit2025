from fastapi import APIRouter, HTTPException
# from typing import List
from Function.MongoDatabase import collection,DB

from Function.models import PriceData, PriceResponse,reqCollection_Name,req
# from crud import create_price, read_prices, read_price, update_price, delete_price

price_router = APIRouter()
@price_router.get("/")
def okRun():
      return {"message": "OK RUNNING"}

# @price_router.post("/prices", response_model=PriceResponse)
# async def create_price_endpoint(data: PriceData):
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



@price_router.post("/create_collection")
async def create_collection(req: reqCollection_Name):
      print("--------------------------------")
      print(req.name) # collection_name
      if req.name in DB.list_collection_names(req):
           return {"message": f"Collection '{req.name}' already exists."}
      DB.create_collection(req.name)
      print("--------------[END]------------------")
      
      return {"message": f"Collection '{req}' created successfully."}