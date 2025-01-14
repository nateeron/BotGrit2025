from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
from typing import AsyncGenerator
import time

from Function.Routes.routes import price_router
from Function.Routes.routes_ConfigBot import r_ConfigBot
from Function.Routes.routes_infoPrice import r_infoPrice
from Function.Routes.routes_BotGrid import r_botgrid
import websocket
import json
from threading import Thread

from websocket import WebSocketApp
# Initialize the FastAPI app
app = FastAPI()

# Add CORS middleware to allow cross-origin requests
origins = [
    "http://127.0.0.1:5500",  # Your frontend server's address
    "http://localhost:5500",
    "http://127.0.0.1:5501/*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include your routers
app.include_router(price_router)
app.include_router(r_ConfigBot)
app.include_router(r_infoPrice)
app.include_router(r_botgrid)


# Create a shared queue for SSE messages
message_queue = asyncio.Queue()


class PriceData(BaseModel):
    price: float


@app.post("/update_price/")
async def update_price(price_data: PriceData):
    """
    Endpoint to update price and notify clients in real-time.
    """
    message = f"Price updated to {price_data.price}"
    await message_queue.put(message)
    print(f"Received price update: {price_data}")
    return {"status": "success", "message": "Price updated successfully", "data": price_data.price}

        
@app.get("/events")
async def get_events() -> StreamingResponse:
    """
    SSE endpoint to stream real-time messages to clients.
    """
    async def event_stream() -> AsyncGenerator[str, None]:
        while True:
            message = await message_queue.get()  # Wait for new message
            yield f"data: {message}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

def start_websocket():
    def on_error(ws, error):
        print('error')
        print(error)

    def on_close(ws):
        print("### closed ###")

    def on_open(ws):
        print("### opened ###")

    def on_message(ws, message):
        # Parse the JSON message
        trade = json.loads(message)
        # Extract the price from the trade message
        # if use @aggTrade or  @trade
        price = float(trade['p']) 

        # if use @kline_
        # price = float(trade['k']['c']) 
        symbo = trade['s']

        print('------------start-------------')
        print(symbo,price)
        #time.sleep(5)
        #**order_manager = FN_buy.OrderManager()  # Create an instance of OrderManager
        #**order_manager.check_price_buy(price,symbo)

        # order_manager = FN_sell.OrderManager()  # Create an instance of OrderManager
        #order_manager.check_price_sell(price,symbo)
        # Call the function to check the price
        #FN_buy.OrderManager.check_price_buy(price,symbo)
        #FN_sell.check_price_sell(price)
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/xrpusdt@trade",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
    
async def start_fastapi():
    import uvicorn
    #uvicorn.run("FastAPI_BotGrid2025:app", host="127.0.0.1", port=45441, reload=1)
    config = uvicorn.Config("FastAPI_BotGrid2025V4:app", host="127.0.0.1", port=45441, reload=1)
    server = uvicorn.Server(config)
    await server.serve()
# async def main():
#     # Run FastAPI and WebSocket concurrently
#     loop = asyncio.get_event_loop()
#     websocket_task = loop.run_in_executor(None, start_websocket)
#     fastapi_task = asyncio.create_task(start_fastapi())

#     await asyncio.gather(websocket_task, fastapi_task)
async def main():
    # Run FastAPI
    #loop = asyncio.get_event_loop()
    fastapi_task = asyncio.create_task(start_fastapi())
    await fastapi_task
# Run the Uvicorn server
if __name__ == "__main__":
    
    #import uvicorn
    #uvicorn.run("FastAPI_BotGrid2025:app", host="127.0.0.1", port=45441, reload=1)

    asyncio.run(main())