
import json

def calAction_Buy(p,config):
    price = float(p)
    
    
    percen = float(config['PERCEN_BUY'])
    
    price_ = price - ((price / 100) * percen) 
    return price_,percen
 
def calAction_Sell(p,config):
    price = float(p)
    percen = float(config['PERCEN_SELL'])
    price_ = price + ((price / 100) * percen) 
    return price_,percen 


def f1(n):
    formatted_quantity = "{:.1f}".format(n)
    return float(formatted_quantity)

def f2(n):
    formatted_quantity = "{:.2f}".format(n)
    return float(formatted_quantity)
    
def f4(n):
    formatted_quantity = "{:.4f}".format(n)
    return float(formatted_quantity)



print(f4(0.4955951))