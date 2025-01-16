from fastapi import APIRouter, Request
from flask import Flask, request
# from Service.crud import create_tables
from Function.Service.crud import create_tables
#from Function.Service.sv_infoPrice import create_tables
from Function.MongoDatabase import ConnetBinace,Config
import ccxt
from pprint import pprint
from binance.client import Client
from datetime import datetime, timedelta

import Function.Service.ConvertTime as cvt
from Function.Models.model_routes_infoPrice import reqGetHistory
import json
import time

r_ConfigBot = APIRouter()

API_KEY_C = ConnetBinace['API_KEY']
API_SECRET = 'gVptG2cBQy0jyieXU0G8c3iucaj2JzFQthcPQYvNdnSwUZFQKK56WfKhwA08Gjs4'# ConnetBinace['API_SECRET']
_client = Client(API_KEY_C, API_SECRET)


@r_ConfigBot.get("/ConfigBot/run")
def run():
        create_tables()
        return {"message": "OK RUNNING ConfigBot"}

@r_ConfigBot.get("/ConfigBot/CheckConfig")
def CheckConfig():
    try:
        # Get the database connection details
        db = Config.connet()
        # Extract the database name
        database_name = db.name
        print(database_name)
        # Extract the host and port details
        client = db.client
        host, port = None, None
        connected = ""
        time.sleep(0.5)
        # If available, extract address details
        if client.address:
            host, port = client.address
        elif host == None and port == None:
            settings = Config.getSetting()  # Call the getSetting method
            host = settings["Connetion"]["DATA_HOST"] 
            port = settings["Connetion"]["DATA_PORT"] 
            connected = " not connet from settings.json"
        # Return the connection details
        return {
            "connection_details": {
                "host": host,
                "port": port,
                "database_name": database_name,
                "status": connected
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@r_ConfigBot.post("/ConfigBot/key")
def key():
    print("API Key: ", API_KEY_C)
    amount_in = '@20'
    side_ = "Buy"
    amount_in = float(amount_in[1:])  # Assuming the format '@20' for amount

    connect_Binance = None
    try:
        # Initialize Binance Client
        _client.get_server_time()  # To test if the connection is working
    except Exception as e:
        text_error = f"! Error connecting to Binance: {str(e)}"
        return {"message": text_error}
    
    symbol_in = 'XRPUSDT'
    symbol_ = None
    try:
        symbol_ = _client.get_symbol_ticker(symbol=symbol_in)['symbol']
        print(symbol_)
    except Exception as e:
        text_error = f"! Error fetching ticker: {symbol_in} | {str(e)}"
        return {"message": str(e)}

    # Split symbol (e.g., 'XRPUSDT' -> ['XRP', 'USDT'])
    unit = symbol_in.split("USDT")  # Adjust based on the symbol format
    Coin_last_Price = _client.get_symbol_ticker(symbol=symbol_in)['price']
    print(Coin_last_Price)
    
    # Handle amount
    amount_in = float(amount_in)

    # Fetch balances for the given symbol units
    Coind_balance_main = ""
    Coind_balance_Secondary = ""
    try:
        Coind_balance_main = _client.get_asset_balance(asset=unit[1])
        print("Main Coin Balance: ", Coind_balance_main)
    except Exception as e:
        pass

    try:
        Coind_balance_Secondary = _client.get_asset_balance(asset=unit[0])
        print("Secondary Coin Balance: ", Coind_balance_Secondary)
    except Exception as e:
        pass

    # Place market order for "Buy" or "Sell"
    side_ = side_.lower()  # "buy" or "sell"
    print(f"Order side: {side_}")
    if side_ == "buy":
        order = _client.order_market_buy(
            symbol=symbol_in,
            quantity=amount_in
        )
    else:
        order = _client.order_market_sell(
            symbol=symbol_in,
            quantity=amount_in
        )
    
    print(order)  # Print the order response for confirmation

    return {"message": "OK RUNNING key"}

@r_ConfigBot.post("/ConfigBot/getBalanceJson")
def getBalanceJson():
    # Initialize the Binance client (make sure you have set your API key and secret)
    
    try:
        # Fetch account balances
        balance_info = _client.get_account()
    except Exception as e:
        return {"message": f"Error fetching balance: {str(e)}"}

    # Extract balances and filter them
    balances = balance_info['balances']
    filtered_balances = []

    for asset in balances:
        
        asset_name = asset['asset']
        free_balance = float(asset['free'])  # Amount available

        # Process balances for XRP, USDT or other assets with non-zero balances
        if free_balance > 0:
            #print(f"Asset: {asset_name}, Free Balance: {free_balance}")
            value_in_usdt = 0
            if asset_name != "USDT":
                try:
                    # Fetch the current price of the asset in USDT
                    price = float(_client.get_symbol_ticker(symbol=f"{asset_name}USDT")['price'])
                    value_in_usdt = free_balance * price
                except Exception as e:
                    value_in_usdt = 0  # Skip if no USDT trading pair
            else:
                value_in_usdt = free_balance  # USDT itself

            # Only keep assets with value greater than $0.01 in USDT
            if value_in_usdt > 0.01:
                filtered_balances.append({
                    "asset": asset_name,
                    "free_balance": free_balance,
                    "value_in_usdt": round(value_in_usdt, 2)
                })

    # Calculate and return total value and item price
    resp = []
    sum_balance = 0

    # Add item price and sort by 'value_in_usdt' in descending order
    for entry in filtered_balances:
        entry['item_price'] = entry['value_in_usdt'] * 35  # Example: Item price calculation in THB

    sorted_balances = sorted(filtered_balances, key=lambda x: x['value_in_usdt'], reverse=True)

    for entry in sorted_balances:
        sum_balance += entry['value_in_usdt']
        
        resp.append({
            "asset": entry['asset'],
            "free_balance": entry['free_balance'],
            "value_in_usdt": entry['value_in_usdt'],
            "item_price": round(entry['item_price'], 2)
        })

    # Add total balance and its equivalent in THB
    resp.append({
        "sum_balance_usdt": round(sum_balance, 2),
        "sum_balance_thb": round(sum_balance * 35, 2)
    })

    return resp

@r_ConfigBot.post("/ConfigBot/getBalance")
def getBalance():
       
        # Fetch account balances
        balance_info = _client.get_account()

        # Extract balances and filter them
        balances = balance_info['balances']
        filtered_balances = []

        for asset in balances:

                asset_name = asset['asset']
                
                free_balance = float(asset['free'])  # Amount available
                if asset_name == 'XRP':
                    print("asset_name",asset_name,free_balance)
                if asset_name == 'USDT':
                    print("asset_name",asset_name,free_balance)   
                if free_balance > 0:

                    # Get the value in USDT for each coin
                    if asset_name != "USDT":
                        try:
                            # Fetch the current price of the asset in USDT
                            price = float(_client.get_symbol_ticker(symbol=f"{asset_name}USDT")['price'])
                            value_in_usdt = free_balance * price
                        except:
                            value_in_usdt = 0  # Skip if no USDT trading pair
                    else:
                        value_in_usdt = free_balance  # USDT itself

                    # Filter assets with value greater than $10
                    if value_in_usdt > 0.01:
                        filtered_balances.append({
                            "asset": asset_name,
                            "free_balance": free_balance,
                            "value_in_usdt": round(value_in_usdt, 2)
                        })
        #resp = []
        #sum_balance = 0
        #sorted_balances = sorted(filtered_balances, key=lambda x: x['value_in_usdt'], reverse=True)
        #for entry in filtered_balances:
        #    sum_balance +=entry['value_in_usdt']
        #    print(f"Asset: {entry['asset']}, Free Balance: {entry['free_balance']}, Value in USDT: {entry['value_in_usdt']}")
        #    resp.append(f"Asset: {entry['asset']}, Free Balance: {entry['free_balance']}, Value in USDT: {entry['value_in_usdt']}")
        #resp.append(f"Sum balance: {(sum_balance):.2f} : THB x35 ={(sum_balance*35):.2f} ")
        #return resp
        resp = []
        sum_balance = 0

        # Add item price and sort by 'value_in_usdt' in descending order
        for entry in filtered_balances:
            entry['item_price'] = entry['value_in_usdt'] * 35  # Example of item price calculation

        # Sort filtered_balances by 'value_in_usdt' in descending order
        sorted_balances = sorted(filtered_balances, key=lambda x: x['value_in_usdt'], reverse=True)

        for entry in sorted_balances:
            sum_balance += entry['value_in_usdt']
            print(
                f"Asset: {entry['asset']}, Free Balance: {entry['free_balance']}, "
                f"Value in USDT: {entry['value_in_usdt']}, Item Price: {entry['item_price']:.2f}"
            )
            resp.append(
                f"Asset: {entry['asset']}, Free Balance: {entry['free_balance']}, "
                f"Value in USDT: {entry['value_in_usdt']}, Item Price: {entry['item_price']:.2f}"
            )

        # Add total balance and its equivalent in THB
        resp.append(f"Sum balance: {sum_balance:.2f} USDT : THB x35 = {sum_balance * 35:.2f}")
        return resp
    
@r_ConfigBot.post("/ConfigBot/gethistoryJson")
def gethistoryJson(req:reqGetHistory):
    # List to hold historical orders
    order_history = []
    err = ""

    try:
        # Loop through all symbols to get their order history
        for symbol in req.symbols:
            try:
                # Fetch all orders for the symbol
                orders = _client.get_all_orders(symbol=symbol, limit=req.limit)
                
                # Limit to the first 3 orders and filter completed buy/sell orders
                i = 0
                for order in orders:
                    if i >= 3:
                        break
                    if order['status'] == 'FILLED' and order['side'] in ['BUY', 'SELL']:
                        executed_qty = float(order['executedQty'])
                        quote_qty = float(order['cummulativeQuoteQty'])
                        price = (
                            f'{(quote_qty / executed_qty):.4f}' if executed_qty > 0 and symbol == 'XRPUSDT' else
                            f'{(quote_qty / executed_qty):.2f}' if executed_qty > 0 else "0.00"
                        )
                        
                        order_info = {
                            "symbol": symbol,
                            "order_id": order['orderId'],
                            "side": order['side'],  # BUY or SELL
                            "price": price,
                            "executed_qty": executed_qty,
                            "quote_qty": quote_qty,
                            "time": cvt.ts_int13_to_datetime_bangkok(int(order['updateTime']))  # Convert timestamp
                        }
                        order_history.append(order_info)
                        i += 1
            except Exception as e:
                print(f"Error fetching orders for {symbol}: {e}")
                err = f"Error fetching orders for {symbol}: {e}"

        # Sort orders by time in descending order
        order_history.sort(key=lambda x: x['time'], reverse=True)

        # Prepare a structured response
        resp = []
        if order_history:
            for order in order_history:
                resp.append({
                    "symbol": order['symbol'],
                    "side": order['side'],
                    "price": order['price'],
                    "executed_qty": order['executed_qty'],
                    "quote_qty": order['quote_qty'],
                    "time": order['time']
                })
        else:
            resp.append({"message": f"No order history found. {err}"})

        return resp
    except Exception as e:
        return {"error": str(e)}
    
@r_ConfigBot.post("/ConfigBot/gethistory")
def getHistory(req:reqGetHistory):
    # List to hold historical orders
    order_history = []
    print(req)
    try:
        # Fetch all trading symbols from the account
        #exchange_info = client.get_exchange_info()
        #symbols = [symbol['symbol'] for symbol in exchange_info['symbols']]
        #symbols = ['XRPUSDT','BNBUSDT']
        # Loop through all symbols to get their order history
        err = ""
        for symbol in req.symbols:
            try:
                # Fetch all orders for the symbol
                orders = _client.get_all_orders(symbol=symbol,limit=req.limit)
                # Filter completed buy/sell orders
                i = 0
                for order in orders:
                    if i <= 3 :
                        i +=1
                    if order['status'] == 'FILLED' and order['side'] in ['BUY', 'SELL']:
                        executed_qty = float(order['executedQty'])
                        quote_qty = float(order['cummulativeQuoteQty'])
                        if symbol == 'XRPUSDT':
                            price = (
                                f'{(quote_qty / executed_qty):.4f}'
                                if executed_qty > 0 else "0.0000"
                            )
                        else:
                            price = (
                                f'{(quote_qty / executed_qty):.2f}'
                                if executed_qty > 0 else "0.00"
                            )   
                        order_info = {
                            "symbol": symbol,
                            "order_id": order['orderId'],
                            "side": order['side'],  # BUY or SELL
                            "price":price,
                            "executed_qty": float(order['executedQty']),
                            "quote_qty": float(order['cummulativeQuoteQty']),
                            "time": cvt.ts_int13_to_datetime_bangkok(int(order['updateTime']) )
                        }
                        order_history.append(order_info)
            except Exception as e:
                print(f"Error fetching orders for {symbol}: {e}")
                err = f"Error fetching orders for {symbol}: {e}"
        # Sort orders by time (optional)
        order_history.sort(key=lambda x: x['time'], reverse=True)
        # Prepare a response summary
        resp = []
        for order in order_history:
            resp.append(f"Symbol: {order['symbol']}, Side: {order['side']}, "
                        f"Price: {order['price']}, Executed Quantity: {order['executed_qty']}, "
                        f"Quote Quantity: {order['quote_qty']}, Time: {order['time']}")
        return resp if resp else [f"No order history found. {err}"]
    
    except Exception as e:
        return {"error": str(e)}
    

# Helper function to convert balances to USDT
def get_balance_in_usdt(asset_name, free_balance):
        
    if asset_name == "USDT":
        return free_balance  # USDT itself
    try:
        price_in_usdt = float(_client.get_symbol_ticker(symbol=f"{asset_name}USDT")['price'])
        return free_balance * price_in_usdt
    except:
        return 0  # If no USDT pair exists

@r_ConfigBot.post("/ConfigBot/getSumary")
def report_Sumary():
        now = datetime.utcnow()
        end_time = now
        start_time = end_time - timedelta(days=30)
        start_time_ms = int(start_time.timestamp() * 1000)
        end_time_ms = int(end_time.timestamp() * 1000)
        snapshots = _client.get_account_snapshot(type='SPOT' ,startTime=start_time_ms,endTime=end_time_ms)#['snapshotVos']
        print(len(snapshots['snapshotVos']))
        print(snapshots['snapshotVos'])
        
        return snapshots

@r_ConfigBot.get('/ConfigBot/getSetting')
def getdata():
    settings =[]
    with open("Setting.js", "r") as js_files:
        js_code = js_files.read()
        # Parse the JSON string into a Python dictionary
        data = js_code.split('=')[1]
        settings = json.loads(data)
    return settings

@r_ConfigBot.post('/ConfigBot/update')
async def update(req: Request):
    req_data = await req.json()
    print(req_data)
    print(type(req_data))
    # Writing request data to Setting.js file
    with open("Setting.js", "w") as js_file:
        js_file.write("var data = " + json.dumps(req_data, indent=4))
    return "Success"
       
