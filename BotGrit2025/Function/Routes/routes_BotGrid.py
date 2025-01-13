from fastapi import APIRouter,HTTPException
from Function.Models.model_routes_botGrid import req_bot,infoPrice,check_price,backtest,GetinfoBacktest
from Function.Service.sv_botgrid import (bot_start)
import Function.Service.sv_botgrid_Backtest as bt 


import json
from datetime import datetime,timedelta
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from bson import ObjectId
import threading
import Function.Service.BotGrit_CheckPrice_Fast_API_FN_buy as FN_buy
import websocket
import asyncio
import websockets
import time


r_botgrid = APIRouter()

ws_thread = None
ws_thread2 = None
ws = None
ws2 = None
should_run = False
should_run2 = False
price1 = [{"E":99999999,'p': 0.0}]

websocket_task = None

    
@r_botgrid.get("/botgrid/run")
def run():
    return {"message": "OK RUNNING Botgrid"}


@r_botgrid.post("/botgrid/start")
def start(req:req_bot):
    
    req = bot_start(req)
    return {"message":req}


def on_error(ws, error):
    print('error')
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    print("### opened ###")

Pass_Run = True

def on_message(ws, message):
    global Pass_Run
    
    if Pass_Run :
        Pass_Run = False
        try:
            data = json.loads(message)
            if price1[0]["E"] != data["E"] and  price1[0]["p"] != data["p"]:
                print(data["s"],data["p"],55)
                print('------------start-------------')
                symbo = data['s']
                price = float(data['p']) 
                T = int(data['T'])
                print(symbo,price)
                order_manager =FN_buy.OrderManager()  # Create an instance of OrderManager
                req = check_price(
                        symbol=symbo,
                        price=price,
                        tf="1m",
                        timestamp=T
                )
                resp = order_manager.check_price_buy(req)
                # {'e': 'trade', 'E': 1722844176552, 's': 'XRPUSDT', 't': 641078642, 'p': '0.47220000', 'q': '1273.00000000', 'T': 1722844176546, 'm': False, 'M': True}
                if price1:
                    price1.pop(0)
                price1.append({"E":data["E"],"p":data["p"]})
        except Exception as e:
            print(f'Error on_message :{e}')
        finally:
            print('The try except is finished')
            time.sleep(2)
            Pass_Run = True
    
def start_websocket_blocking():
    global ws
    # Blocking WebSocket logic
    ws = websocket.WebSocketApp(
        "wss://stream.binance.com:9443/ws/xrpusdt@trade",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.on_open = on_open
    ws.run_forever()
    
async def websocket_handler():
    uri = "wss://stream.binance.com:9443/ws/xrpusdt@trade"
    async with websockets.connect(uri) as websocket:
        print("WebSocket Connection Opened")
        try:
            async for message in websocket:
                data = json.loads(message)
                if price1[0]["E"] != data["E"] and  price1[0]["p"] != data["p"]:
                    print(data["s"],data["p"],55)
                    print('------------start-------------')
                    symbo = data['s']
                    price = float(data['p']) 
                    print(symbo,price)
                    order_manager =FN_buy.OrderManager()  # Create an instance of OrderManager
                    resp = await order_manager.check_price_buy(price,symbo)
                    # {'e': 'trade', 'E': 1722844176552, 's': 'XRPUSDT', 't': 641078642, 'p': '0.47220000', 'q': '1273.00000000', 'T': 1722844176546, 'm': False, 'M': True}
                    if price1:
                        price1.pop(0)
                    price1.append({"E":data["E"],"p":data["p"]})
        except websockets.ConnectionClosed as e:
            print("WebSocket Closed:", e)
            
async def start_websocket():
    global websocket_task
    if websocket_task and not websocket_task.done():
        print("WebSocket is already running.")
        return
    loop = asyncio.get_event_loop()
    websocket_task = loop.run_in_executor(None, start_websocket_blocking)
    # websocket_task = asyncio.create_task(websocket_handler())
    print("WebSocket started.")
    
async def stop_websocket():
    global  ws
    if ws is not None:
        ws.close()
    return JSONResponse(content={"message": "WebSocket connection stopped"})
 
@r_botgrid.post("/botgrid/startBot")
async def startBot_websocket():
    await start_websocket()
    return {"message": "WebSocket startBot"}


@r_botgrid.post("/botgrid/stop")
async def stopWebsocket():
    await stop_websocket()
    return JSONResponse(content={"message": "WebSocket connection stopped"})

@r_botgrid.post("/botgrid/Backtest")
async def Backtest(req:backtest):
    #1 Loda price
    #2 loop Check price
    #3 save price action
    #4 show output and calcurate
    resp = bt.Backtest_start(req)
    return resp

@r_botgrid.post("/botgrid/data_Backtest")
async def data_Backtest(req:GetinfoBacktest):
    print("data_Backtest")
    resp = bt.data_Backtest(req)
    return resp