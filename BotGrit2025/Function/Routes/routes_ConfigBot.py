from fastapi import APIRouter
# from Service.crud import create_tables
from Function.Service.crud import create_tables

r_ConfigBot = APIRouter()
@r_ConfigBot.get("/ConfigBot/run")
def run():
        create_tables()
        return {"message": "OK RUNNING ConfigBot"}
