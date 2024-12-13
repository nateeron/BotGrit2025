from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:4500")
DB = client["BotGrit2025"]
collection = DB["BNBUSDT_1m"]
