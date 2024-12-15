from fastapi import FastAPI
from Function.Routes.routes import price_router
from Function.Routes.routes_ConfigBot import r_ConfigBot
from Function.Routes.routes_infoPrice import r_infoPrice


import uvicorn


app = FastAPI()

# Include the router for price-related endpoints
app.include_router(price_router)
app.include_router(r_ConfigBot)
app.include_router(r_infoPrice)


@app.on_event("startup")
async def startup_event():
    print("FastAPI app started")

if __name__ == "__main__":
    #uvicorn.run("FastAPI_BotGrid2025:app", host="127.0.0.1", port=45441, reload=True)
    uvicorn.run("FastAPI_BotGrid2025:app", host="127.0.0.1", port=45441, reload=True)

# uvicorn FastAPI_BotGrid2025:app --reload
# uvicorn FastAPI_BotGrid2025:app --reload --port 45441