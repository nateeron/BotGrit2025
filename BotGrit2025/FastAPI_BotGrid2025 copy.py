from fastapi import FastAPI
from Function.Routes.routes import price_router
from Function.Routes.routes_ConfigBot import r_ConfigBot
from Function.Routes.routes_infoPrice import r_infoPrice
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
import socketio
from pydantic import BaseModel


# Initialize Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins=["http://127.0.0.1:5500/Note_Test/TESTSocketIO/","http://127.0.0.1:5500", "http://localhost:5500"])

# Initialize FastAPI app
app = FastAPI()


# Add CORS middleware before wrapping the app with Socket.IO
origins = [
    "http://127.0.0.1:5500/",  #http://127.0.0.1:5500/ Allow requests from this origin
    "http://localhost:5500/",
    "http://127.0.0.1:5500/Note_Test/TESTSocketIO/",# Another example for localhost
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow only specific origins
    allow_credentials=True,
    allow_methods=["*"],    # Allow all HTTP methods
    allow_headers=["*"],    # Allow all headers
)

# Include your routers
app.include_router(price_router)
app.include_router(r_ConfigBot)
app.include_router(r_infoPrice)

class PriceData(BaseModel):
    price: float
# Real-time event to emit updated price info
@app.post("/update_price/")
async def update_price(price_data: PriceData):
    """
    Endpoint to update price and notify clients in real-time.
    """
    print(price_data)
    # Notify all connected clients about the updated price
    await sio.emit("price_update", price_data.price)
    return {"status": "success", "message": "Price updated successfully", "data": price_data.price}

app = socketio.ASGIApp(sio, app)




# Create a separate Socket.IO event handler
@sio.event
async def get_price_update(sid, data):
    await sio.emit('price_update', {'price': 123.45}, to=sid)

# Run the app with Uvicorn
if __name__ == "__main__":
    uvicorn.run("FastAPI_BotGrid2025:app", host="10.88.88.132", port=45441, reload=True)
