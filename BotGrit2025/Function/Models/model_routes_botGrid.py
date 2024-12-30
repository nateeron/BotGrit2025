
from pydantic import BaseModel

class req_bot(BaseModel):
    id: int
    name: str
    #symbol: str
    #tf: str
    #orderVal: float
    #actionBuy:float
    #tp:float
    #alert:bool
    #alertTo:str
  
class insertOrder_(BaseModel):
    SYMBOL: str
    PRICE_BUY: str 
    PRICE_SELL: str
    QUANTITY: str
    STATUS: int 
    DATE_BUY: str
    DATE_SELL: str
    
class oj_Order(BaseModel):
    Order_id: int
    OrderName: str
    symbol: str
    timestem: int
    priceAction: float
    Buy_Quantity: float
    Buy_Amount: float
    Buy_SumQuantity: float
    Buy_SumAmount: float
    priceSell: float
    Sell_Quantity: float
    Sell_Amount: float
    Sell_SumQuantit: float
    Sell_SumAmount: float
    CreateDate: str
    UpdateDate: str
    isDelete: int
    isActive: int
    MainOrder: int# 0-999999
    SubOrder: int# 0-999999