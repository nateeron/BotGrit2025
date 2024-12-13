from bson import ObjectId
from pymongo.collection import Collection

# Helper function to convert MongoDB document to dictionary
def document_to_dict(doc):
    return {
        "id": str(doc["_id"]),
        "Timestem": doc["Timestem"],
        "Open": doc["Open"],
        "High": doc["High"],
        "Low": doc["Low"],
        "Close": doc["Close"]
    }

# CRUD operations
def create_price(collection: Collection, data: dict):
    result = collection.insert_one(data)
    return document_to_dict(collection.find_one({"_id": result.inserted_id}))

def read_prices(collection: Collection):
    prices = list(collection.find())
    return [document_to_dict(price) for price in prices]

def read_price(collection: Collection, id: str):
    record = collection.find_one({"_id": ObjectId(id)})
    return document_to_dict(record) if record else None

def update_price(collection: Collection, id: str, data: dict):
    result = collection.update_one({"_id": ObjectId(id)}, {"$set": data})
    return result.matched_count > 0

def delete_price(collection: Collection, id: str):
    result = collection.delete_one({"_id": ObjectId(id)})
    return result.deleted_count > 0


