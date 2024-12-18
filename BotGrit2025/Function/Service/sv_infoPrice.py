
from Function.MongoDatabase import db
from Function.Models.model_routes_infoPrice import req_getprice
import asyncio
import requests

from datetime import datetime,timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed




base_url = "https://api.binance.com/api/v3/klines"
interval = '1m' 

def convert(timestamp):
    # Convert milliseconds to seconds
    timestamp_sec = timestamp / 1000
    # Convert to datetime
    date_time = datetime.utcfromtimestamp(timestamp_sec)
    # Format datetime as string
    return date_time.strftime("%Y-%m-%d %H:%M:%S")

def load_date(table):
   
    # Retrieve documents from MongoDB collection
    resp = list(db[table].find({}, {"timestamp": 1,"Create_Date":1, "close": 1}).sort("timestamp", -1))
    # Map over the response and convert timestamp
    result = []

    # Loop through the response and convert timestamp
    for s in resp:
        # Add formatted timestamp to the document
        #s['dateT'] = convert(s.get('timestamp'))
        ss= convert(s.get('timestamp'))
        cs= (s.get('Create_Date'))
        result.append(str(ss)+'|'+str(cs))
    return result

def getprice_Api():
    
    
    pass
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
    resp = list(db[table_collection].find().sort("timestamp", -1))
    
    # ถ้า ไม่มี data ให้ Getdata
    if resp == []:
    #if True:
        lastEndTime = 0
        lengtbar_ = 3
        limit_ = 3
        get_data(req,req.symbol,lengtbar_,limit_,lastEndTime)
        resp = list(db[table_collection].find())
    else:
        endbar = len(resp)-1
        data_start_time = resp[endbar]['timestamp']/1000
        data_last_time = resp[0]['timestamp']/1000
        print('----------------------------------------------------------------')
        req_strptime_start = dateTime_To_timestamp(req.datefrom)
        req_strptime_last = dateTime_To_timestamp(req.dateto)

        print('S>',(req_strptime_start))
        print('S>',(req_strptime_last))
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_timestamp =dateTime_To_timestamp(current_time)
        print('--------current_time--------------------------------------------------------')
        calbar = 0
        print(CaldateTime(current_timestamp))
        print(CaldateTime(req_strptime_last))
        if current_timestamp > req_strptime_last:
            calbar = dateTime_To_timestamp(current_time) - req_strptime_last
            if calbar > 60:
                calbar = int(calbar/60)
                print('calbar:',calbar)
        print('----------------------------------------------------------------')
        lengtbar_ = calbar
        
        limit_ = 1000 if calbar >= 1000 else calbar
        lastEndTime = req_strptime_last
        #get_data(req,req.symbol,lengtbar_,limit_,lastEndTime)
        
     
    return resp
   

def load_data(symbol, interval, limit, lastEndTime):
    print('----------------------------------------------------------------')
    print('load_data',symbol, interval, limit, lastEndTime)
    EndTime = 0 # dateTime_To_timestamp(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print('----------------------------------------------------------------')
    params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
    # 'limit': limit
    utc =  7*60*60*1000
    # [lastEndTime]----------------------------------------------------------------
    if lastEndTime != 0 and 1==1:
        # เวลา ที่ดึงมาจะ -7 bangkok
        print('ts:',lastEndTime)
        if len(str(lastEndTime)) < 13:
            lastEndTime = ((lastEndTime) * 1000 - utc )
        else:
            lastEndTime = ((lastEndTime) - utc )
        print('ts convert:',lastEndTime)

        params['startTime'] = lastEndTime
    # [EndTime]----------------------------------------------------------------
    if EndTime != 0 and 1==1:
        if len(str(EndTime)) < 13:
            EndTime = ((EndTime) * 1000 - utc )
        else:
            EndTime = ((EndTime) - utc )
        params['endTime'] = EndTime    
            
    print('base_url',base_url, params)
    response = requests.get(base_url, params=params)
    data = []
    if response.status_code == 200:
        data = response.json()
    for x in data:
        print(x[0]+utc)
        x[0] += utc
    print('----------------------------------------------------------------')
    
    return data

def dateTime_To_timestamp(date_string):
    # date_string = "17-12-2025 15:35"
    date_object = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    bangkok = 7*60*60
    timestamp = int(date_object.timestamp()+bangkok)
    return timestamp

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
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for row in data:
        # Map row data to a dictionary
        oj = {
            "timestamp": row[0],  # Open time
            "open": row[1],
            "high": row[2],
            "low": row[3],
            "close": row[4],
            "volume": row[5],
            "Create_Date": current_time,
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
    if lengtbar_ >0 and num_batches == 0:
        num_batches = 1
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
    
  