
from pydantic import BaseModel

class req_getprice(BaseModel):
    symbol: str
    tf: str
    getAll: bool
    datefrom: str
    dateto: str
    limit: int
    ohlc:str # o | h |c | l | all
    
class resp_price(BaseModel):
    _id: object
    timestem: str
    open: float
    high: float
    low: float
    close: float
    volume:int 
class IsUpdate:
    Empty = 1
    Update = 2
    Load = 3
    
class DeleteRequest(BaseModel):
    tableName: str
    
class reqGetHistory(BaseModel):
    symbols: list
    limit:int
    
    