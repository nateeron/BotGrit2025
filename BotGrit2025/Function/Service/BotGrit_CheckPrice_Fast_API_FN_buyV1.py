import json
import datetime
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


class OrderManager:
    def __init__(self):
        with open('config.json') as f:
            config = json.load(f)
        self.config = config
        
        
    def check_price_buy(self,pri,symbol):
        try:
            priceActionLast = 999999999.99
            price = float(pri)
            status = 0 #| 0 = not Sell
            orderby = "DATE_SELL" #  SYMBOL, PRICE_BUY, PRICE_SELL, STATUS, DATE_BUY, DATE_SELL 
            limit = 1
            table_collection = "OrderBuy"
            # Get data last Buy
            order_json = list(db[table_collection].find().sort("timestamp", -1))    
            # order_json = qury.Select_tableOrder(status,symbol,orderby,limit)
            if order_json != []:
                #order_json = order_json
                order = json.loads(order_json) if order_json else None
                if order:
                    status = order[0]['status'] # from SQL data
                    # ถ้ายังไม่ขาย ให้นับจุดซื้อล่าสุด ลงมา
                    if status == 1:
                        priceActionLast = float(order[0]['Price_Sell'])
                    else:
                        priceActionLast = float(order[0]['Price'])
               
                
            # Check buy 
            next_Buy,percenB =  ta.calAction_Buy(priceActionLast,self.config)
            
            next_Buy = ta.f4(next_Buy)
            
            print('#######[ Check Buy ]#######')
            print('is :',price <= next_Buy)
            # ถ้าขาย ได้ไม้คืน จุกซื้อถึดไปจะนับจากจุดขายล่าสุด ลงมา 
            print("price <= next_Buy: ",price ,'<=',next_Buy ,' %percenB :',percenB ,' priceActionLast :',priceActionLast)
            
            status = 0 #| 0 = not Sell
            orderby = "DATE_SELL" #  SYMBOL, PRICE_BUY, PRICE_SELL, STATUS, DATE_BUY, DATE_SELL 
            limit = 3
            # Check Sell id, SYMBOL, PRICE_BUY, PRICE_SELL,QUANTITY, STATUS, DATE_BUY, DATE_SELL 
            OrderSell = list(db[table_collection].find({"STATUS":status,"SYMBOL":symbol}).sort(orderby, 1).limit(limit))   
            # OrderSell = qury.Select_tableOrder(status,symbol,orderby,limit)
            
            if price <= next_Buy :
            #if True:
                print("Action BUY")
                order_quantity =float(self.config['ORDER_VAL'])
                #  buy  sell
                Price_Action =2.15 #BotSpot.trad(symbol,'buy',order_quantity,'','','')
                # # เมื่อซื้อเสร็จ ให้ SAVE ราคาขาย
                quantity = ta.f2( order_quantity/price )
                P_Sell ,percenS =  ta.calAction_Sell(Price_Action,self.config)
                # SYMBOL, PRICE_BUY, PRICE_SELL, STATUS, DATE_BUY
                STATUS = 0
                s = oj_Order
                s.Order_id = 123 
                req = fn_insertOrder(s)
                #qury.Insert_tableOrder(symbol, Price_Action,ta.f4(P_Sell),STATUS,quantity)
                    
            
            print('#######[ Check Sell ]#######')
           
            for item in OrderSell:
                print('IF Market > mySell')
                print( price,'>=', item['Price_sell'],price >= float(item['Price_sell']))
                
                if price >= float(item['Price_sell']) :
                    print("Action SELL")
                    Price_Action =BotSpot.trad(symbol,'sell',item['Quantity'],'','','')
                    priceSell = price
                    new_status = 1 
                    s = oj_Order
                    s.Order_id = 555 
                    req = update_order_status()
                    # qury.update_order_status(item['OrderActionID'],new_status,priceSell)
        except Exception as e:
            print('An exception occurred',e)




order_manager_ = OrderManager()
order_manager_.check_price_buy('0.5508','XRPUSDT')
# current_timestamp = time.time()
# print(current_timestamp)
# current_datetime = datetime.datetime.fromtimestamp(current_timestamp)
# print(current_datetime.strftime('%Y-%m-%d %H:%M:%S'))
    