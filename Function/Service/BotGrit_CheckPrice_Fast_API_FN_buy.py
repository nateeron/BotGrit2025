import json
from datetime import datetime
import time
# Load the JSON data from the file
import pprint as pprint
import Function.Service.FN_calAction as ta

from Function.MongoDatabase import Config
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
db= Config.connet()
from bson import ObjectId

class MongoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)  # Convert ObjectId to string
        return super().default(obj)


def convert_timestamp(timestamp:int):
    """convert

    Args:
        timestamp (int): 1734591480000

    Returns:
        str : 19/12/2567 6:58:00
    """
    # Convert milliseconds to seconds
    timestamp_sec = timestamp / 1000
    # Convert to datetime
    date_time = datetime.utcfromtimestamp(timestamp_sec)
    # Format datetime as string
    return date_time.strftime("%Y-%m-%d %H:%M:%S")

def Action_Buy(req:oj_Order,table_collection):
    
    order_dict = req.dict()
    db[table_collection].insert_one(order_dict)
class ASDF(BaseModel):
    Oder_NaverBuy:int
    

Oder_NaverBuy = 0
count_Buy = 0
befo_price = []
class OrderManager:
    
    def __init__(self):
        pass
        # with open('config.json') as f:
        #     config = json.load(f)
        self.config = ""
        
    def check_price_buy(self,req:check_price):
        
        ss = 0
        global Oder_NaverBuy
        global befo_price
        global count_Buy
        # ราคา ปิด จากกราฟ
        """req
        symbol='XRPUSDT' 
        price=2.1095 
        tf='1m' 
        timestamp=1735722360000
        """
        #print('check_price_buy',req)
        # ซื้อ
        #--------------------------------------------------------------
        # 001 เช็ก Data ว่ามี order ล่าสุด Action ที่กี่ usd
        # 002 ถ้าไม่มี Action order ให้ set ราคาเริ่มต้น 
        # 003 ถ้ามี Action order ให้เช็กว่า ซื้อ หรือขาย แล้ว นำราคา ที่ Action มาเป็นจุดซื้อถัดไป
        # 004 กรณี ขายหมด แล้วราคาขึ้น ไม่มีจังหวะซื้อ 
        # 005 เช็ก Sell
        price = float(req.price)
        befo_price_ = 0
        if len(befo_price) == 0:
            befo_price.append(price)
            
        elif len(befo_price) == 1:
            befo_price_ = befo_price[0]
            
            befo_price.append(price)
        elif len(befo_price) == 2:
            befo_price_ = befo_price[0]
            befo_price.pop(0)
            befo_price.append(price)
            
        st = Config.getSetting()
        db= Config.connet()
        amount = float(st["ORDER_VAL"])
        percenB = float(st["PERCEN_BUY"])
        percenS = float(st["PERCEN_SELL"])
        print(f"amount {amount} PERCEN_BUY {percenB} PERCEN_SELL {percenS}")
        qty ="{:.4f}".format(float(amount/price) )
        P_Sell = price + ((price / 100) * percenS) 
        #--------------------------------------------------------------
        # 001
        table_collection = 'OrderBuy'
        order_last = list(db[table_collection].find().sort("UpdateDate", -1).limit(3))  
        #if len(order_last) != 0:  
        #    print(order_last[0])
        #    print(order_last[len(order_last)-1])
        price_start = 0
        # ใน data -7 *1000
        timestem_buy = req.timestamp 
        time_now = convert_timestamp(timestem_buy) 
        actionB = False
        #--------------------------------------------------------------
        # 002
        if len(order_last) == 0:
            price_start = req.price
            
            # Action Binace Buy and Get Time
            
            order = oj_Order(
                            Order_id=1,
                            status=0,
                            OrderName="xrp tf1m test",
                            symbol=req.symbol,
                            timestem_buy=timestem_buy,
                            timestem_sell=timestem_buy,
                            priceAction=price_start,
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
            Action_Buy(order,table_collection)
            actionB = True
            count_Buy += 1
            # print(count_Buy,req.price)
        else:
            #---------------------------------------------------------
            # 003
            Position = "BUY" if order_last[0]['status'] == 0 else "SELL" 
            if Position == "BUY":
                price_start =  order_last[0]['priceAction']
            elif Position == "SELL":
                price_start =  order_last[0]['priceSell']
                
            P_Buy = price_start - ((price_start / 100) * percenB) 
            order = oj_Order(
                            Order_id=1,
                            status=0,
                            OrderName="xrp tf1m test",
                            symbol=req.symbol,
                            timestem_buy=timestem_buy,
                            timestem_sell=timestem_buy,
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
               
            # 2.1191104000000003
            # 2.1432 2.1434143999999997
            
            if req.price <= P_Buy :
                #print(price_start)
                #print(req.price ,"<= ",P_Buy,"=",req.price <= P_Buy)
                #ASDF.Oder_NaverBuy = 0
                Oder_NaverBuy = 0
                Action_Buy(order,table_collection)
                actionB = True
                count_Buy += 1
                # print(count_Buy,req.price)
            else:
                #--------------------------------------------------------------
                # 004
                order_last = list(db[table_collection].find({"status":0}).limit(3)) 
                if Oder_NaverBuy > 20:
                    #ASDF.Oder_NaverBuy = 0
                    Oder_NaverBuy = 0
                    print("***Oder_NaverBuy****")
                    print(Oder_NaverBuy)
                    Action_Buy(order,table_collection)
                    actionB = True
                P_Buys = price_start + ((price_start / 100) * percenB) 
                crossunder = befo_price[0] >= befo_price[1]
                if len(order_last) == 0 :#and req.price >= P_Buys :
                    # Oder_NaverBuy += 1
                    # print("Oder_NaverBuy : >>>>>>>>>>>>> ",req.price)
                    Action_Buy(order,table_collection)
                    count_Buy += 1
                    # print(count_Buy,req.price)
                
        #----------------------------------------------------------------------
        # 005
        if not actionB:
            OrderSell = list(db[table_collection].find({"status":0,"symbol":req.symbol}).sort("priceSell", 1).limit(10))   
            
            #print("-----------------")
            
            #for item in OrderSell:
            #    a = item['priceAction']
            #    b ="{:.4f}".format(item['priceSell'])
            #    bd = item['priceSell']
            #    c = item['CreateDate']
            #    print(a,b,c)
            for item in OrderSell:
                if req.price >= float(item['priceSell']) :
                    update_data = {
                            "status": 1,
                            "timestem_sell": req.timestamp,
                            "priceSell": req.price,
                            "Sell_Quantity": item['Sell_Quantity'],
                            "UpdateDate": time_now,  # current timestamp for UpdateDate
                        }
                    document_id = ObjectId(item["_id"])
                        # Update the document in the collection
                    db[table_collection].update_one(
                            {"_id": document_id},  # Query to find the document by _id
                            {"$set": update_data}  # Update fields with the new data
                        )
        