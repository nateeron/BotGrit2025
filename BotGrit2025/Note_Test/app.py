from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
client = MongoClient('localhost', 27017)
db = client['BotGrit2025']

def create_table():
    """
    Create MongoDB collections (tables) for the required structure.
    """
    # Create collections if they do not exist
    for collection_name in ["XRPUSDT_1m", "BNBUSDT_1m", "OrderBuy", "ConfigBot"]:
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
            print(f"Collection {collection_name} created.")


def check_and_create_tables():
    """
    Check if required tables exist and create them if they don't.
    """
    create_table()


def create_entry(collection_name, data):
    """
    Insert a document (row) into a collection (table).
    """
    result = db[collection_name].insert_one(data)
    return result.inserted_id


def read_entries(collection_name, query=None):
    """
    Retrieve documents (rows) from a collection (table).
    """
    if query is None:
        query = {}
    return list(db[collection_name].find(query))


def update_entry(collection_name, query, update_data):
    """
    Update a document (row) in a collection (table).
    """
    result = db[collection_name].update_one(query, {'$set': update_data})
    return result.modified_count


def delete_entry(collection_name, query):
    """
    Delete a document (row) from a collection (table).
    """
    result = db[collection_name].delete_one(query)
    return result.deleted_count

# Example table schemas
def initialize_tables():
    check_and_create_tables()

    # Example data for XRPUSDT_1m
    if db['XRPUSDT_1m'].count_documents({}) == 0:
        create_entry("XRPUSDT_1m", {
            "timestem": datetime.utcnow(),
            "O": 0.0,
            "h": 0.0,
            "l": 0.0,
            "c": 0.0
        })

    # Example data for BNBUSDT_1m
    if db['BNBUSDT_1m'].count_documents({}) == 0:
        create_entry("BNBUSDT_1m", {
            "timestem": datetime.utcnow(),
            "O": 0.0,
            "h": 0.0,
            "l": 0.0,
            "c": 0.0
        })

    # Example data for OrderBuy
    if db['OrderBuy'].count_documents({}) == 0:
        create_entry("OrderBuy", {
            "id": 1,
            "orderName": "ExampleOrder",
            "Symbol": "BTCUSDT",
            "timestem": datetime.utcnow(),
            "priceAction": 1000.0,
            "Buy_Quantity": 1.0,
            "Buy_Amount": 1000.0,
            "Buy_SumQuantity": 1.0,
            "Buy_SumAmount": 1000.0,
            "priceSell": 0.0,
            "Sell_Quantity": 0.0,
            "Sell_Amount": 0.0,
            "Sell_SumQuantity": 0.0,
            "Sell_SumAmount": 0.0,
            "CreateDate": datetime.utcnow(),
            "UpdateDate": datetime.utcnow(),
            "isDelete": False,
            "isActive": True,
            "MainOrder": 1,
            "SubOrder": 0
        })

    # Example data for ConfigBot
    if db['ConfigBot'].count_documents({}) == 0:
        create_entry("ConfigBot", {
            "StrategyName": "DefaultStrategy",
            "PercenBuy": 0.1,
            "PercenSell": 0.1,
            "DateCreate": datetime.utcnow(),
            "DateUpdate": datetime.utcnow(),
            "Isactive": True,
        })

if __name__ == "__main__":
    initialize_tables()

    # Example usage of CRUD functions
    print("All entries in XRPUSDT_1m:", read_entries("XRPUSDT_1m"))

    update_entry("ConfigBot", {"StrategyName": "DefaultStrategy"}, {"PercenBuy": 0.15})
    print("Updated ConfigBot:", read_entries("ConfigBot"))

    delete_entry("XRPUSDT_1m", {"O": 0.0})
    print("After deletion, XRPUSDT_1m:", read_entries("XRPUSDT_1m"))
