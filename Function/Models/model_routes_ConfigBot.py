from pydantic import BaseModel

# Pydantic models for validation
class PriceData(BaseModel):
    Timestem: int
    Open: float
    High: float
    Low: float
    Close: float

class PriceResponse(PriceData):
    id: str


class reqCollection_Name(BaseModel):
    name: str
    
class req(BaseModel):
    name: str