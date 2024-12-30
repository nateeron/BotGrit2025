from fastapi import APIRouter,HTTPException
from Function.Models.model_routes_botGrid import req_bot
from Function.Service.sv_botgrid import (bot_start)

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
    websocket_task = asyncio.create_task(websocket_handler())
    print("WebSocket started.")
    
async def stop_websocket():
    global websocket_task
    if websocket_task:
        websocket_task.cancel()
        try:
            await websocket_task
        except asyncio.CancelledError:
            print("WebSocket task cancelled.")
        websocket_task = None
        
        
@r_botgrid.post("/botgrid/startBot")
async def startBot_websocket():
    await start_websocket()
    return {"message": "WebSocket stopped"}



@r_botgrid.post("/botgrid/stop")
async def stopWebsocket():
    await stop_websocket()
    return JSONResponse(content={"message": "WebSocket connection stopped"})


    


