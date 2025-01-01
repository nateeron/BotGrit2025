import json
from datetime import datetime
import time
# Load the JSON data from the file
import pprint as pprint
import Function.Service.FN_calAction as ta

from Function.MongoDatabase import db
from Function.Models.model_routes_botGrid import oj_Order
from Function.Service.sv_botgrid import (fn_insertOrder,update_order_status)
import Function.Service.BotSpot as  BotSpot

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

class OrderManager:
    
    def __init__(self):
        with open('config.json') as f:
            config = json.load(f)
        self.config = config
        
    def check_price_buy(self,pri,symbol,time_action = 0,ver=""):
        isDebug = True
        try:
            priceActionLast = 999999999.99
            price = float(pri)
            status = 0 #| 0 = not Sell
            orderby = "DATE_SELL" #  SYMBOL, PRICE_BUY, PRICE_SELL, STATUS, DATE_BUY, DATE_SELL 
            limit = 1
            
            table_collection = "OrderBuy"#+ver
            # Get data last Buy
            order_json = list(db[table_collection].find().sort("timestamp", -1))    
            # order_json = qury.Select_tableOrder(status,symbol,orderby,limit)
            if order_json != []:
                #order_json = order_json
                order = order_json #json.loads(order_json, cls=MongoEncoder) if order_json else None
                if order:
                    status = order[0]['status'] # from SQL data
                    # ถ้ายังไม่ขาย ให้นับจุดซื้อล่าสุด ลงมา
                    if status == 1:
                        priceActionLast = float(order[0]['priceSell'])
                    else:
                        priceActionLast = float(order[0]['priceAction'])
               
                
            # Check buy 
            next_Buy,percenB =  ta.calAction_Buy(priceActionLast,self.config)
            
            next_Buy = ta.f4(next_Buy)
            
            #print('#######[ Check Buy ]#######')
            #print('is :',price <= next_Buy)
            # ถ้าขาย ได้ไม้คืน จุกซื้อถัดไปจะนับจากจุดขายล่าสุด ลงมา 
            #print("price <= next_Buy: ",price ,'<=',next_Buy ,' %percenB :',percenB ,' priceActionLast :',priceActionLast)
            
            status = 0 #| 0 = not Sell
            orderby = "DATE_SELL" #  SYMBOL, PRICE_BUY, PRICE_SELL, STATUS, DATE_BUY, DATE_SELL 
            limit = 3
            # Check Sell id, SYMBOL, PRICE_BUY, PRICE_SELL,QUANTITY, STATUS, DATE_BUY, DATE_SELL 
            OrderSell = list(db[table_collection].find({"status":status,"symbol":symbol}).sort(orderby, 1).limit(limit))   
            # OrderSell = qury.Select_tableOrder(status,symbol,orderby,limit)
            
            if price <= next_Buy and time_action != 0 :
            #if True:
                #print("Action BUY")
                order_quantity =float(self.config['ORDER_VAL'])
                #  buy  sell
                Price_Action =price #BotSpot.trad(symbol,'buy',order_quantity,'','','')
                # # เมื่อซื้อเสร็จ ให้ SAVE ราคาขาย
                quantity = ta.f2( order_quantity/price )
                P_Sell ,percenS =  ta.calAction_Sell(Price_Action,self.config)
                # SYMBOL, PRICE_BUY, PRICE_SELL, STATUS, DATE_BUY
                STATUS = 0
                bangoko = 7*60*60*1000
                time_now = convert_timestamp(time_action+bangoko) if isDebug else  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                timestamp_now =time_action+bangoko if isDebug else datetime.now().timestamp()
                
                order = oj_Order(
                            Order_id=1,
                            status=0,
                            OrderName="xrp tf1m test",
                            symbol=symbol,
                            timestem_buy=timestamp_now,
                            timestem_sell=timestamp_now,
                            priceAction=Price_Action,
                            Buy_Quantity=quantity,
                            Buy_Amount=0,
                            Buy_SumQuantity=0,
                            Buy_SumAmount=0,
                            priceSell=P_Sell,
                            Sell_Quantity=quantity,
                            Sell_Amount=0,
                            Sell_SumQuantit=1.0,
                            Sell_SumAmount=50500.0,
                            CreateDate=time_now,
                            UpdateDate=time_now,
                            isDelete=0,
                            isActive=1,
                            MainOrder=0,
                            SubOrder=0
                        )
                order_dict = order.dict()
                db[table_collection].insert_one(order_dict)
                #qury.Insert_tableOrder(symbol, Price_Action,ta.f4(P_Sell),STATUS,quantity)
                    
            
            #print('#######[ Check Sell ]#######')
           
            for item in OrderSell:
                #print('IF Market > mySell')
                #print( price,'>=', item['priceSell'],price >= float(item['priceSell']))
                if price >= float(item['priceSell']) :
                    #print("Action SELL")
                    Price_Action = float(item['priceSell']) #BotSpot.trad(symbol,'sell',item['Sell_Quantity'],'','','')
                    priceSell = price
                    new_status = 1 
                    s = oj_Order
                    s.Order_id = 555 
                    #req = update_order_status()
                    
                    time_now = convert_timestamp(time_action) if isDebug else  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    timestamp_now =time_action if isDebug else datetime.now().timestamp()
                    document_id = ObjectId(item["_id"])  # _id of the document you want to update
                    # New data to update
                    update_data = {
                        "status": 1,
                        "timestem_sell": timestamp_now,
                        "priceSell": Price_Action,
                        "Sell_Quantity": item['Sell_Quantity'],
                        "Sell_Amount": 0,
                        "Sell_SumQuantit": 0,
                        "Sell_SumAmount": 0,
                        "UpdateDate": time_now,  # current timestamp for UpdateDate
                    }

                    # Update the document in the collection
                    result = db[table_collection].update_one(
                        {"_id": document_id},  # Query to find the document by _id
                        {"$set": update_data}  # Update fields with the new data
                    )
                    # qury.update_order_status(item['OrderActionID'],new_status,priceSell)
                    
            # กรณี
        except Exception as e:
            # H:\Developer\Python\BotGrit2025\BotGrit2025\Function\Service\BotGrit_CheckPrice_Fast_API_FN_buy.py
            print('Error :BotGrit_CheckPrice_Fast_API_FN_buy.py :',e)




# order_manager_ = OrderManager()
# order_manager_.check_price_buy('0.5508','XRPUSDT')
# current_timestamp = time.time()
# print(current_timestamp)
# current_datetime = datetime.datetime.fromtimestamp(current_timestamp)
# print(current_datetime.strftime('%Y-%m-%d %H:%M:%S'))
    