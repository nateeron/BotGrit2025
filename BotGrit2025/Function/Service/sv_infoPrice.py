
from Function.MongoDatabase import db
from Function.Models.model_routes_infoPrice import req_getprice
import asyncio
import requests

from datetime import datetime,timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed




base_url = "https://api.binance.com/api/v3/klines"
interval = '1m' 

def convert(timestamp:int):
    """convert

    Args:
        timestamp (int): 1734591480000

    Returns:
        str : 19/12/2567 6:58:00
    """
    # Convert milliseconds to seconds
    timestamp_sec = timestamp / 1000
    # Convert to datetime
    date_time = datetime.utcfromtimestamp(timestamp_sec)
    # Format datetime as string
    return date_time.strftime("%Y-%m-%d %H:%M:%S")

def load_date(table):
    """_summary_

    Args:
        table (str): 'XRPUSDT_1m'

    Returns:
        List<str>: [
                    "2024-12-17 20:20:00|2024-12-19 13:32:52",
                    "2024-12-17 20:21:00|2024-12-19 13:32:52",
                    "2024-12-17 20:22:00|2024-12-19 13:32:52",
                    "2024-12-17 20:23:00|2024-12-19 13:32:52",
                    ]
    """
    # Retrieve documents from MongoDB collection
    resp = list(db[table].find({}, {"timestamp": 1,"Create_Date":1, "close": 1}).sort("Create_Date", -1))
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


def timeLoadAPI(datefrom):
    """datefrom = "2024-12-19 13:57:00" convert to int 1734591420000 (- 7 Bangkok) """
    return  dateTime_To_timestamp(datefrom) *1000- (7*60*60 *1000)
def getprice_Api():
    
    
    pass




########################################################################################################
########################################################################################################
def LoadPrice(req:req_getprice):
    
    """
    https://api.binance.com/api/v3/klines?symbol=XRPUSDT&interval=1m&limit=1
    https://api.binance.com/api/v3/klines?symbol=BNBUSDT&interval=1m&limit=1
    
    [
        Response Example
        [
            [0]1591258320000,      	// Open time\n
            [1]"9640.7",       	 	// Open\n
            [2]"9642.4",       	 	// High\n
            [3]"9640.6",       	 	// Low\n
            [4]"9642.0",      	 	 	// Close (or latest price)\n
            [5]"206", 			 		// Volume\n
            [6]1591258379999,       	// Close time\n
            [7]"2.13660389",    		// Base asset volume\n
            [8]48,             		// Number of trades\n
            [9]"119",    				// Taker buy volume\n
            [10]"1.23424865",      		// Taker buy base asset volume\n
            [11]"0" 					// Ignore.\n
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
    resp = list(db[table_collection].find().sort("timestamp", 1))
    
    # ถ้า ไม่มี data ให้ Getdata
    if resp == []:
    #if True:
        lastEndTime = 0
        lengtbar_ = 3
        limit_ = 3
        get_data(req,req.symbol,lengtbar_,limit_,lastEndTime)
        resp = list(db[table_collection].find())
    else:
        # Load Update Price
        
        endbar = len(resp)-1
        data_start_time = resp[0]['timestamp']/1000
        data_last_time = int(resp[endbar]['timestamp']/1000)
        print('----------------------------------------------------------------')
        req_strptime_start = timeLoadAPI(req.datefrom)
        req_strptime_end = timeLoadAPI(req.dateto)

        print('S>','DATA:',data_last_time,'GET req:',(req_strptime_start))
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(current_time)
        current_timestamp =timeLoadAPI(current_time)
        print('--------current_time--------------------------------------------------------')
        calbar = 0
        print(CaldateTime(current_timestamp/1000))
        print(CaldateTime(req_strptime_end/1000))
        #print(CaldateTime(req_strptime_last))
        lengtbar_ = 0
        if current_timestamp > req_strptime_end:
           calbar = current_timestamp - req_strptime_end
           if calbar > 60000:
               lengtbar_ = calbar/60000
               lengtbar_s = calbar%60000
               lengtbar_ss = int(calbar/60000)
               print(lengtbar_s,2%2,12%5,lengtbar_ss,lengtbar_)
               print('calbar:',lengtbar_)
        print('----------------------------------------------------------------')
        
        limit_ = 1000 if calbar >= 1000 else calbar
        starttime = req_strptime_start
        endtime = req_strptime_start
        #get_data(req,req.symbol,lengtbar_,limit_,starttime ,endtime)
        
     
    return resp
   ########################################################################################################
   ########################################################################################################
   ########################################################################################################
   ########################################################################################################




def load_data_SETTime(symbol, interval, limit, lastEndTime):
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
    # [EndTime] ----------------------------------------------------------------
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
    # This Convert Time+7
    #for x in data:
    #    print(x[0]+utc)
    #    x[0] += utc
    
    return data


########################################################################################################
########################################################################################################
def load_data(symbol, interval, limit, startTime,EndTime):
    ''' symbol = 'XRPUSDT', 
        interval = '1m', 
        limit = 1000, 
        startTime = 1734591420000,
        EndTime   = 1734591540000

        [Output]
        [
            [
                [0]1591258320000,      	// Open time\n
                [1]"9640.7",       	 	// Open\n
                [2]"9642.4",       	 	// High\n
                [3]"9640.6",       	 	// Low\n
                [4]"9642.0",      	 	 	// Close (or latest price)\n
                [5]"206", 			 		// Volume\n
                [6]1591258379999,       	// Close time\n
                [7]"2.13660389",    		// Base asset volume\n
                [8]48,             		// Number of trades\n
                [9]"119",    				// Taker buy volume\n
                [10]"1.23424865",      		// Taker buy base asset volume\n
                [11]"0" 					// Ignore.\n
            ],\n
        ]\n
    '''
    params = {
            'symbol': symbol,
            'interval': interval,
        }
    
    if limit > 0 :
        params['limit'] = limit
        
    if startTime != 0 and 1==1:
        params['startTime'] = startTime
    if EndTime != 0 and 1==1:
        params['endTime'] = EndTime
    response = requests.get(base_url, params=params)
    data = []
    if response.status_code == 200:
        data = response.json()
    
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
########################################################################################################
########################################################################################################

def get_data(req:req_getprice,symbol_,lengtbar_ ,limit_ ,starttime = 0 ,endtime = 0):
    print('------------------------------------------------------------')
    print('get_data : ',lengtbar_ ,limit_ ,starttime)
    print('get_data CaldateTime: ',CaldateTime(starttime))
    print('------------------------------------------------------------')
    """
    lengtbar_ = bar ราคาทั้งหมด ที่จะ Load 
    limit_ = จำนวน bar ที่ Load แต่ละรอบ
    num_batches = จำนวน รอบที่ Load
    
    """ 
    num_batches = int(lengtbar_ / limit_)
    data_ALL = []
    print("download.....")
    loadTime= []
    if lengtbar_ >0 and num_batches == 0:
        num_batches = 1
    # หาค่า เวลา แล้วกระจาย Load
    for _ in range(num_batches):
        
        if _ == 0 and starttime == 0:
            # --------------------------------------------------
            x = load_data(symbol_, req.tf, limit_, startTime)
            data_ALL.extend(x)  # Use extend to add elements of x to data_ALL
            
            if len(x) > 0 :
                """
                limit_ = 3
                interval = (18)
                example [0],1,2,[3],4,5,[6],7,8,[9],10,11,[12],13,14,[15],16,17,(18 start),(on data 19,20,21,22,23,24,25)
                loadTime = [15,12,9,6,3,0]
                resp =  [15,16,17],
                        [12,13,14],
                        [9 ,10,11],
                        [6 ,7 ,8 ],
                        [3 ,4 ,5 ],
                        [0 ,1 ,2 ]
                """
                st = StartNewTime(interval, limit_)
                startTime = x[0][0] - st
                loadTime.append(startTime)
            # --------------------------------------------------
        else:
            if starttime != 0 :
                # 1723104392000
                # 1723104387
                # print(starttime,CaldateTime(starttime))
                st = StartNewTime(interval, limit_)
                if len(str(starttime)) < 13:
                    starttime = starttime *1000
                loadTime.append(starttime- st)
                #print(loadTime[0],CaldateTime(loadTime[0]/1000))
                starttime = 0
            else:
                st = StartNewTime(interval, limit_)
                startTime = loadTime[len(loadTime)-1] - st
                loadTime.append(startTime)
            
    # print(loadTime)
    
    # Create Task Get API Multi Task max_workers:20 
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
    
  