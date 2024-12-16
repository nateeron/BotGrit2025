
from Function.MongoDatabase import db
from Function.Models.model_routes_infoPrice import req_getprice
import asyncio
import requests

from datetime import datetime,timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed




base_url = "https://api.binance.com/api/v3/klines"
interval = '1m' 

def LoadPrice(req:req_getprice):
    
    """
    https://api.binance.com/api/v3/klines?symbol=XRPUSDT&interval=1m&limit=1
    https://api.binance.com/api/v3/klines?symbol=BNBUSDT&interval=1m&limit=1
    [
        Response Example
  [
    1591258320000,      	// Open time
    "9640.7",       	 	// Open
    "9642.4",       	 	// High
    "9640.6",       	 	// Low
    "9642.0",      	 	 	// Close (or latest price)
    "206", 			 		// Volume
    1591258379999,       	// Close time
    "2.13660389",    		// Base asset volume
    48,             		// Number of trades
    "119",    				// Taker buy volume
    "1.23424865",      		// Taker buy base asset volume
    "0" 					// Ignore.
  ]
]
    Retrieve documents (rows) from a collection (table).
    """
    print("*******ok Call Function *******")
    print(req)
    print(req.datefrom)
    # collection_name = ''
    # if query is None:
    #     query = {}
    # return list(db[collection_name].find(query))
    """Connet DATA """
    table_collection = req.symbol+'_'+req.tf 
    # Output XRPUSDT_1m
    print("table_collection:",table_collection)
    query = None
    if query is None:
        query = {}
    resp = list(db[table_collection].find())
    # print(resp)
    # ถ้า ไม่มี data ให้ Getdata
    if resp == []:
        lastEndTime = 0
        lengtbar_ = 10000
        get_data(req,req.symbol,lengtbar_,1000,lastEndTime)
        resp = list(db[table_collection].find())
        
     
    return resp
   

def load_data(symbol, interval, limit, lastEndTime):
    
    params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
    if lastEndTime != 0:
        params['startTime'] = lastEndTime
        
    response = requests.get(base_url, params=params)
    data = []
    if response.status_code == 200:
        data = response.json()
    
    return data

def CaldateTime(timestamp):
    # Convert the timestamp to a datetime object
    original_datetime = datetime.fromtimestamp(timestamp)
    return original_datetime
def StartNewTime(interval, factor):
    # Define the number of seconds per interval unit
    intervalUnits = {
        's': 1,         # Seconds
        'm': 60,        # Minutes
        'h': 3600,      # Hours
        'd': 86400,     # Days
        'w': 604800     # Weeks
    }
    
    # Parse the interval to get the number and the unit
    intervalValue = int(interval[:-1])
    intervalUnit = interval[-1]
    
    # Calculate the total number of milliseconds
    totalMilliseconds = intervalValue * intervalUnits[intervalUnit] * factor * 1000
    
    return totalMilliseconds

def SortData(data):
    sortedData = sorted(data, key=lambda x: x[0])
    return sortedData

def insert(table_collection, data):
    """
    Insert data into the specified MongoDB collection.

    Parameters:
        table_collection (str): The name of the MongoDB collection.
        data (list of lists): A list of rows, where each row is a list of values.

    Returns:
        InsertManyResult or InsertOneResult: The result of the insert operation.
    """
    ojData = []
    for row in data:
        # Map row data to a dictionary
        oj = {
            "timestem": row[0],  # Open time
            "open": row[1],
            "high": row[2],
            "low": row[3],
            "close": row[4],
            "volume": row[5]
        }
        ojData.append(oj)
    
    # Check if multiple rows or a single row
    if len(ojData) == 1:
        # Insert a single document
        result = db[table_collection].insert_one(ojData[0])
    else:
        # Insert multiple documents
        result = db[table_collection].insert_many(ojData)
    
    return result
    
def get_data(req:req_getprice,symbol_,lengtbar_ ,limit_ ,starttime = 0 ):
    print('------------------------------------------------------------')
    print('get_data : ',lengtbar_ ,limit_ ,starttime)
    print('get_data CaldateTime: ',CaldateTime(starttime))
    print('------------------------------------------------------------')
    num_batches = int(lengtbar_ / limit_)
    data_ALL = []
    lastEndTime = 0
    print("download.....")
    loadTime= []
    # หาค่า เวลา แล้วกระจาย Load
    for _ in range(num_batches):
        
        if _ == 0 and starttime == 0:
            # --------------------------------------------------
            x = load_data(symbol_, req.tf, limit_, lastEndTime)
            data_ALL.extend(x)  # Use extend to add elements of x to data_ALL
            
            if len(x) > 0 :
                st = StartNewTime(interval, limit_)
                lastEndTime = x[0][0] - st
                loadTime.append(lastEndTime)
            # --------------------------------------------------
        else:
            if starttime != 0 :
                # 1723104392000
                # 1723104387
                print(starttime,CaldateTime(starttime))
                st = StartNewTime(interval, limit_)
                loadTime.append((int(starttime)*1000)- st)
                print(loadTime[0],CaldateTime(loadTime[0]/1000))
                
                starttime = 0
            else:
                st = StartNewTime(interval, limit_)
                lastEndTime = loadTime[len(loadTime)-1] - st
                loadTime.append(lastEndTime)
            
    # print(loadTime)
    
    # Use concurrent futures for batch requests
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_time = {executor.submit(load_data, symbol_, interval, limit_, time): time for time in loadTime}
        for future in as_completed(future_to_time):
            time = future_to_time[future]
            try:
                data = future.result()
                data_ALL.extend(data)
               
            except Exception as e:
                print(f"Request failed for time {time}: {e}")
    #print(CaldateTime(time))
    
    # for item in data_ALL:
    #     print(CaldateTime(item[0]))
    print("SortData ...")
    resp = SortData(data_ALL)
    print("download Success...")
    # for item in resp:
    #     print(CaldateTime(item[0]))
    #------------------------------------
    table_collection = req.symbol+'_'+req.tf 
    insert(table_collection,resp)
    return resp
    
  