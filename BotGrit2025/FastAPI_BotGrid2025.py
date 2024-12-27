from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
from typing import AsyncGenerator
import time
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


# Run the Uvicorn server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=45441, reload=True)
