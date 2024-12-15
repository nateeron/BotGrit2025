
from pydantic import BaseModel

class req_getprice(BaseModel):
    table_name: str
    getAll: bool
    datefrom: str
    dateto: str
    ohcl:str # o | h |c | l | all
    
