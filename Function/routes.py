from fastapi import APIRouter

price_router = APIRouter()
@price_router.get("/")
def okRun():
      return {"message": "OK RUNNING"}

