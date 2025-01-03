import json
from datetime import datetime
import time
# Load the JSON data from the file
import pprint as pprint
import Function.Service.FN_calAction as ta

from Function.MongoDatabase import db
from Function.Models.model_routes_botGrid import oj_Order,check_price
from Function.Service.sv_botgrid import (fn_insertOrder,update_order_status)
import Function.Service.BotSpot as  BotSpot
from pydantic import BaseModel
# with open('data.json') as f:
#     data = json.load(f)

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
max_Order = 0
def Action_Buy(req:oj_Order,table_collection):
    data_New.append(req)
    #order_dict = req.dict()
    #db[table_collection].insert_one(order_dict)
    


class OrderManager:
    
    def __init__(self):
        self.data_New = []  # Simulated order data
        self.befo_price = []
        self.Oder_NaverBuy = 0
        self.count_Buy = 0
        self.id_counter = 0

        # Load configuration
        with open('config.json') as f:
            self.config = json.load(f)
            
            
    def action_buy(self, order):
        """Simulate saving an order."""
        self.data_New.append(order)
        print(f"Order Added: {order}")
        
        
    def check_price_buy(self,req:check_price):
        """Process buy logic."""
        price = float(req.price)
        self.id_counter += 1
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
            self.Oder_NaverBuy += 1
            
            if self.Oder_NaverBuy > 20:
                order = oj_Order(
                                Order_id=id+1,
                                status=0,
                                OrderName="xrp tf1m test",
                                symbol=req.symbol,
                                timestem_buy=req.timestamp,
                                timestem_sell=req.timestamp,
                                priceAction=req.price,
                                Buy_Quantity=qty,
                                Buy_Amount=0,
                                Buy_SumQuantity=0,
                                Buy_SumAmount=0,
                                priceSell=P_Sell,
                                Sell_Quantity=qty,
                                Sell_Amount=0,
                                Sell_SumQuantit=0,
                                Sell_SumAmount=0,
                                CreateDate=time_now,
                                UpdateDate=time_now,
                                isDelete=0,
                                isActive=1,
                                MainOrder=0,
                                SubOrder=0
                            )

                #order_last = list(db[table_collection].find({"status":0}).limit(3)) 
            order_last = [x for x in self.data_New if x.status == 0]
            max_Order =  len(order_last) if max_Order < len(order_last)  else max_Order
            if len(order_last) == 0 :
                Action_Buy(order,table_collection)
                count_Buy += 1
        
        if not actionB:
            OrderSell =sorted([x for x in self.data_New if x.status == 0],key=lambda x: x.priceSell,reverse=True)
            # OrderSell = list(db[table_collection].find({"status":0,"symbol":req.symbol}).sort("priceSell", 1).limit(10))   
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
                        if order.Order_id == item.Order_id:  # Match `Order_id`
                            order.status = update_data["status"]
                            order.timestem_sell = update_data["timestem_sell"]
                            order.priceSell = update_data["priceSell"]
                            order.Sell_Quantity = update_data["Sell_Quantity"]
                            order.UpdateDate = update_data["UpdateDate"]
                            break
        return max_Order,self.data_New