from fastapi import APIRouter
from flask import Flask, request
# from Service.crud import create_tables
from Function.Service.crud import create_tables
from Function.MongoDatabase import ConnetBinace
import ccxt

r_ConfigBot = APIRouter()
@r_ConfigBot.get("/ConfigBot/run")
def run():
        create_tables()
        return {"message": "OK RUNNING ConfigBot"}

@r_ConfigBot.post("/ConfigBot/key")
def key():
        print(ConnetBinace["API_KEY"])
        amount_in = '@20'
        side_ = "Buy"
        amount_in = float(amount_in[1:])
        API_KEY_C = ConnetBinace['API_KEY']
        API_SECRET = 'gVptG2cBQy0jyieXU0G8c3iucaj2JzFQthcPQYvNdnSwUZFQKK56WfKhwA08Gjs4'# ConnetBinace['API_SECRET']
    
        connect_Binance = None
    
        try:
                connect_Binance = ccxt.binance({
                    'apiKey': API_KEY_C,
                    'secret': API_SECRET,
                    'enableRateLimit': True,
                    'type': 'spot'
                })
                connect_Binance.load_time_difference()
        
        except:
                text_error = '! error connect_Binace : "apiKey" '
                return {"message": "OK RUNNING key"}
        symbol_in = 'XRP/USDT'
        symbol_ = None
        try:
                symbol_ = connect_Binance.fetch_ticker(symbol_in)['symbol']  # FTMUSDT FTM/USDT
                print(symbol_)
        except Exception as e:
                text_error = '! error format : "symbol[2]" : ' + \
                symbol_in + '| ' + str(e)
                return {"message": str(e)}
        
        unit = symbol_.split("/")
        Coind_last_Price = connect_Binance.fetch_ticker(
        symbol_in)['last']  # ราคาเหรียญล่าสุด
        print(Coind_last_Price)
        quantity_coind = 0.0
    
        amount_in = float(amount_in)
    
        coin_main_last = 0.0

        if unit[1] != 'USDT':
                coin_main_last = connect_Binance.fetch_ticker(
                unit[1]+'USDT')['last']
                print(coin_main_last)
                
        else:
                pass
        Coind_balance_main = ""
        Coind_balance_Secondary = ""
        try:
            # จำนวน Coind กลัก BTCUSDT =  (USDT)  : FTMBNB = (BNB) ที่ถือ
                Coind_balance_main = connect_Binance.fetch_total_balance()[unit[1]]
                print(Coind_balance_main)
                
        # จำนวน Coind รอง BTCUSDT =  (BTC) : FTMBNB = (FTM)  ที่ถือ
        except exception as e:
            pass
        
        try:
                Coind_balance_Secondary = connect_Binance.fetch_total_balance()[unit[0]]
                print(Coind_balance_Secondary)
        #Coind_balance_main = 424.20536
        # ซื้อ n% ของเงินที่มี

        except exception as e:
            pass

        side_ = side_.lower()
        print(side_)