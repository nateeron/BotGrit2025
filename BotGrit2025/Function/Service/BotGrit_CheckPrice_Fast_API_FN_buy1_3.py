import json
from datetime import datetime
import time
# Load the JSON data from the file
from pprint import pprint
import Function.Service.FN_calAction as ta

from Function.MongoDatabase import Config
from Function.Models.model_routes_botGrid import oj_Order,check_price
from Function.Service.sv_botgrid import (fn_insertOrder,update_order_status)
import Function.Service.BotSpot as  BotSpot
from pydantic import BaseModel
# with open('data.json') as f:
#     data = json.load(f)
db= Config.connet()
# # Save the updated JSON data back to the file
# with open('data.json', 'w') as f:
#     json.dump(data, f, indent=4) # Save with indentation for better readability
    
# # Extract the "Order" list from the data
# orders = data["Order"]
# cound = len(orders)
# print('cound1 : ',cound)
# # Filter orders where the "buy" value is greater than or equal to 0.5455
# filtered_orders = [order for order in orders if float(order["buy"]) == 64564 or float(order["buy"]) == 6457764 ]
# cound2 = len(filtered_orders)
# print('cound2 : ',cound2)
# print('data : ',filtered_orders)
# Print the filtered orders
# for order in filtered_orders:
#     print(order)
ISDOING_ACTION = 0

from bson import ObjectId

class MongoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)  # Convert ObjectId to string
        return super().default(obj)


def convert_timestamp(timestamp: int):
    """Convert milliseconds timestamp to readable string format."""
    timestamp_sec = timestamp / 1000
    date_time = datetime.utcfromtimestamp(timestamp_sec)
    return date_time.strftime("%d/%m/%Y %H:%M:%S")

Oder_NaverBuy = 0
count_Buy = 0
befo_price = []
id = 0
data_New = []

def Action_Buy(self,req:oj_Order,table_collection):
    data_New.append(req)
    self.data_New.append(req)
    #order_dict = req.dict()
    #db[table_collection].insert_one(order_dict)
    


class OrderManager:
    
    def __init__(self):
        self.data_New = []  # Simulated order data
        self.befo_price = []
        self.Oder_NaverBuy = 0
        self.count_Buy = 0
        self.id_counter = 0
        self.max_Order = 0
        
        # Load configuration
        with open('config.json') as f:
            self.config = json.load(f)
            
            
    def action_buy(self, order):
        """Simulate saving an order."""
        self.data_New.append(order)
        self.id_counter += 1
        
        
    def check_price_buy(self,data):
        """
        For BackTEST Fast"""
        
        for ind,x in enumerate(data):
            
            if ind % 100000 == 0:
                print("Count:",ind,"Data Langth:",len(self.data_New))
                
            price = x['close']
            #print(x)
            time_action = x['timestamp']
            req = check_price(
                    symbol='XRPUSDT',
                    price=price,
                    tf="1m",
                    timestamp=time_action
            )
            """Process buy logic."""

            price = float(req.price)
            time_now = convert_timestamp(req.timestamp)

            if len(self.befo_price) < 2:
                self.befo_price.append(price)
            else:
                self.befo_price.pop(0)
                self.befo_price.append(price)


            amount = 25
            percenS = 1.5
            percenB = 0.8

            qty ="{:.4f}".format(float(amount/price) )
            P_Sell = price + ((price / 100) * percenS) 

            table_collection = 'OrderBuy'
            #order_last = list(db[table_collection].find().sort("UpdateDate", -1).limit(3))  
            order_last = len(self.data_New)
            
            price_start = price if order_last == 0 else self.data_New[-1]['priceAction']
            

            actionB = False
            P_Buy = price_start - (price_start / 100) * percenB
            if order_last == 0 or price <= P_Buy:
                order = {
                    "Order_id": self.id_counter,
                    "status": 0,
                    "OrderName": "xrp tf1m test",
                    "symbol": req.symbol,
                    "timestem_buy": req.timestamp,
                    "timestem_sell": req.timestamp,
                    "priceAction": price,
                    "Buy_Quantity": qty,
                    "Buy_Amount": 0,
                    "Buy_SumQuantity": 0,
                    "Buy_SumAmount": 0,
                    "priceSell": P_Sell,
                    "Sell_Quantity": qty,
                    "Sell_Amount": 0,
                    "Sell_SumQuantity": 0,
                    "Sell_SumAmount": 0,
                    "CreateDate": time_now,
                    "UpdateDate": time_now,
                    "isDelete": 0,
                    "isActive": 1,
                    "MainOrder": 0,
                    "SubOrder": 0
                }
                self.action_buy(order)
                
                self.count_Buy += 1
                actionB = True
                self.Oder_NaverBuy =0
            else:

                if self.Oder_NaverBuy > 20:
                    order = {
                        "Order_id": self.id_counter,
                        "status": 0,
                        "OrderName": "xrp tf1m test",
                        "symbol": req.symbol,
                        "timestem_buy": req.timestamp,
                        "timestem_sell": req.timestamp,
                        "priceAction": price,
                        "Buy_Quantity": qty,
                        "Buy_Amount": 0,
                        "Buy_SumQuantity": 0,
                        "Buy_SumAmount": 0,
                        "priceSell": P_Sell,
                        "Sell_Quantity": qty,
                        "Sell_Amount": 0,
                        "Sell_SumQuantity": 0,
                        "Sell_SumAmount": 0,
                        "CreateDate": time_now,
                        "UpdateDate": time_now,
                        "isDelete": 0,
                        "isActive": 1,
                        "MainOrder": 0,
                        "SubOrder": 0
                    }
                    self.action_buy(order)
                    self.count_Buy += 1
                    actionB = True
                    self.Oder_NaverBuy =0
                    #order_last = list(db[table_collection].find({"status":0}).limit(3))
                    #print(self.data_New) 
                try:
                    order_last = [x for x in self.data_New if x.get("status") == 0]
                except Exception as e:
                  print('Error order_last ',e)
                  print(self.data_New)
               
                self.max_Order =  len(order_last) if self.max_Order < len(order_last)  else self.max_Order
                if len(order_last) == 0 :
                    self.Oder_NaverBuy += 1
                    
                    #self.action_buy(order,table_collection)
                    #self.count_Buy += 1
                    #actionB = True
                    #self.Oder_NaverBuy =0
                    

            if not actionB:
                OrderSell =sorted([x for x in self.data_New if x.get("status") == 0],key=lambda x: x.get("priceSell"),reverse=True)
                for item in OrderSell:
                    if req.price >= float(item['priceSell']) :
                        update_data = {
                                "status": 1,
                                "timestem_sell": req.timestamp,
                                "priceSell": req.price,
                                "Sell_Quantity": item['Sell_Quantity'],
                                "UpdateDate": time_now,  
                            }
                        for order in self.data_New:
                            if order['Order_id'] == item['Order_id']:  # Match `Order_id`
                                order["status"] = update_data["status"]
                                order["timestem_sell"] = update_data["timestem_sell"]
                                order["priceSell"] = update_data["priceSell"]
                                order["Sell_Quantity"] = update_data["Sell_Quantity"]
                                order["UpdateDate"] = update_data["UpdateDate"]
                                break
        #print(self.max_Order)
        if isinstance(self.data_New, list):
            if len(self.data_New) > 0:
                db[table_collection].insert_many(self.data_New)
        else:
            db[table_collection].insert_one(self.data_New)
        return self.max_Order