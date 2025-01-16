from fastapi import APIRouter
# from typing import List
from Function.MongoDatabase import Config 

db= Config.connet()

price_router = APIRouter()
@price_router.get("/")
def okRun():
      return {"message": "OK RUNNING"}


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