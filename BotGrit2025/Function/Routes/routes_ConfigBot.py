from fastapi import APIRouter
from flask import Flask, request
# from Service.crud import create_tables
from Function.Service.crud import create_tables
#from Function.Service.sv_infoPrice import create_tables
from Function.MongoDatabase import ConnetBinace
import ccxt
import pprint as pprint
from binance.client import Client
from datetime import datetime, timedelta



r_ConfigBot = APIRouter()

API_KEY_C = ConnetBinace['API_KEY']
API_SECRET = 'gVptG2cBQy0jyieXU0G8c3iucaj2JzFQthcPQYvNdnSwUZFQKK56WfKhwA08Gjs4'# ConnetBinace['API_SECRET']
client = Client(API_KEY_C, API_SECRET)


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
        except Exception as e:
            pass
        
        try:
                Coind_balance_Secondary = connect_Binance.fetch_total_balance()[unit[0]]
                print(Coind_balance_Secondary)
        #Coind_balance_main = 424.20536
        # ซื้อ n% ของเงินที่มี

        except Exception as e:
            pass
       # trades = connect_Binance.fetch_order_trades(symbol=symbol_in)
        s = connect_Binance.fetch_balance()
        print(s)
        side_ = side_.lower()
        print(side_)
        
@r_ConfigBot.post("/getBalance")
def getBalance():
       
        # Fetch account balances
        balance_info = client.get_account()

        # Extract balances and filter them
        balances = balance_info['balances']
        filtered_balances = []

        for asset in balances:

                asset_name = asset['asset']
                
                free_balance = float(asset['free'])  # Amount available
                if asset_name == 'XRP':
                    print("asset_name",asset_name,free_balance)
                if asset_name == 'USDT':
                    print("asset_name",asset_name,free_balance)   
                if free_balance > 0:

                    # Get the value in USDT for each coin
                    if asset_name != "USDT":
                        try:
                            # Fetch the current price of the asset in USDT
                            price = float(client.get_symbol_ticker(symbol=f"{asset_name}USDT")['price'])
                            value_in_usdt = free_balance * price
                        except:
                            value_in_usdt = 0  # Skip if no USDT trading pair
                    else:
                        value_in_usdt = free_balance  # USDT itself

                    # Filter assets with value greater than $10
                    if value_in_usdt > 0.01:
                        filtered_balances.append({
                            "asset": asset_name,
                            "free_balance": free_balance,
                            "value_in_usdt": round(value_in_usdt, 2)
                        })
        resp = []
        sum_balance = 0
        for entry in filtered_balances:
            sum_balance +=entry['value_in_usdt']
            print(f"Asset: {entry['asset']}, Free Balance: {entry['free_balance']}, Value in USDT: {entry['value_in_usdt']}")
            resp.append(f"Asset: {entry['asset']}, Free Balance: {entry['free_balance']}, Value in USDT: {entry['value_in_usdt']}")
        resp.append(f"Sum balance: {(sum_balance):.2f} : THB x35 ={(sum_balance*35):.2f} ")
        return resp

# Helper function to convert balances to USDT
def get_balance_in_usdt(asset_name, free_balance):
        
    if asset_name == "USDT":
        return free_balance  # USDT itself
    try:
        price_in_usdt = float(client.get_symbol_ticker(symbol=f"{asset_name}USDT")['price'])
        return free_balance * price_in_usdt
    except:
        return 0  # If no USDT pair exists

@r_ConfigBot.post("/getSumary")
def report_Sumary():
        now = datetime.utcnow()
        end_time = now
        start_time = end_time - timedelta(days=30)
        start_time_ms = int(start_time.timestamp() * 1000)
        end_time_ms = int(end_time.timestamp() * 1000)
        snapshots = client.get_account_snapshot(type='SPOT' ,startTime=start_time_ms,endTime=end_time_ms)#['snapshotVos']
        print(len(snapshots['snapshotVos']))
        print(snapshots['snapshotVos'])
        
        return snapshots
       
       
