from pymongo import MongoClient
import json
# MongoDB connection
# client = MongoClient("mongodb://localhost:4500")


class Config:
    """
    from Function.MongoDatabase import Config \n
    db= Config.connet()
    """
    @staticmethod
    def getSetting():
        # Open the JavaScript file
        with open("Setting.js", "r") as js_file:
            js_code = js_file.read()
            # Remove the variable assignment (e.g., 'settings = ')
            json_start_index = js_code.find('=') + 1
            json_string = js_code[json_start_index:].strip()
            # Parse the JSON string into a Python dictionary
            settings = json.loads(json_string)
            return settings

    @staticmethod
    def connet():
        settings = Config.getSetting()  # Call the getSetting method
        host = settings["Connetion"]["DATA_HOST"]
        port = settings["Connetion"]["DATA_PORT"]
        DB_Name = settings["Connetion"]["DATA_NAME"]
        user = settings["Connetion"]["DATA_USER"]
        passw = settings["Connetion"]["DATA_PASSWORD"]
        client = None
        if user != "" and passw != "" :
            client = MongoClient(f"mongodb://{user}:{passw}@{host}:{port}/admin")
        else :
            client = MongoClient(f"mongodb://{host}:{port}")
        db = client[DB_Name]
        return db

       
# try:
#     db = Config.connet()
#     print("Successfully connected to the database.")
# except Exception as e:
#     print(f"Error: {e}")
    
ConnetBinace= {
        "API_KEY": "YcPKKIzIXkYec2bT2ecKQSrFNauM1X99WlOjCpcqxeD8leTvLOR1KsyZxDm6ZYSC",
        "API_SECRET": "",
        "LINE_ADMIN": "GBUXdDrBPOmT8vELYFXZUSmLnDI3gG4mLeJqUXIQh1o",
        "LINE_ADMIN2": "VYsjukEYGyIiRGXCUqhTZKSxRfCUe9c1eDhSbY5Lf28"
    }

