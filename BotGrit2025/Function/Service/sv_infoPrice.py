
from Function.MongoDatabase import Config
from Function.Models.model_routes_infoPrice import req_getprice,IsUpdate,DeleteRequest
import asyncio
import requests

from datetime import datetime,timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

db= Config.connet()
## TS: int10 to datetime
## TS: int13 to datetime
## TS: int10 to datetime bangkok
## TS: int13 to datetime bangkok
## TS: datetime to int10
## TS: datetime to int13
## TS: datetime to int10 bangkok
## TS: datetime to int13 bangkok
base_url = "https://api.binance.com/api/v3/klines"
interval = '1m' 

def convert_timestamp(timestamp:int):
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

def load_dates(table):
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
    resp = list(db[table].find({}, {"timestamp": 1,"Create_Date":1, "close": 1}).sort("timestamp", -1))
    # Map over the response and convert timestamp
    result = []

    # Loop through the response and convert timestamp
    for s in resp:
        # Add formatted timestamp to the document
        #s['dateT'] = convert(s.get('timestamp'))
        df= (s.get('timestamp'))
        ss= convert_timestamp(s.get('timestamp'))
        bk= convert_timestamp(s.get('timestamp')+(7*60*60*1000))
        cs= (s.get('Create_Date'))
        result.append(str(df)+','+str(ss)+','+str(bk)+'|'+str(cs))
    return result

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
    resp = list(db[table].find({}, {"timestamp": 1,"Create_Date":1, "close": 1}).sort("timestamp", -1))
    # Map over the response and convert timestamp
    result = []
    result_oj = []
    result_ojson ={}
    count = 0 
    loop =1
    print(len(resp))
    # Loop through the response and convert timestamp
    for index, s in enumerate(resp):
        count += 1
        
        # Add formatted timestamp to the document
        #s['dateT'] = convert(s.get('timestamp'))
        df= (s.get('timestamp'))
        ss= convert_timestamp(s.get('timestamp'))
        bk= convert_timestamp(s.get('timestamp')+(7*60*60*1000))
        cs= (s.get('Create_Date'))
        #result_oj.append(str(index)+" "+str(df)+','+str(ss)+','+str(bk)+'|'+str(cs))
        #result_oj.append(index)
        
        result_ojson[str(df)+"_"+str(index+1)+"_"+str(count)] = (str(bk)+' ,'+str(ss)+'|'+str(cs))
        #result_oj[str(df)+"_"+str(index)] = (str(ss)+','+str(bk)+'|'+str(cs))
        if index == 0:
                info = {
                    "Data Langth": len(resp),
                    "Data Oject number ": f"{(len(resp)/1000):.2f}" ,
                }
                result.append(info)
        if count == 1000 :
            
            result.append(result_ojson)
            result_oj = []   # Reset the chunk
            result_ojson ={}  # Reset the chunk
            count = 0
        if len(resp) ==  loop:
            print(len(resp),loop)
            result.append(result_ojson)
          
        loop+=1
    return result

def timeLoadAPI(datefrom):
    """datefrom = "2024-12-19 13:57:00" convert to int 1734591420000 (- 7 Bangkok) """
    return  dateTime_To_timestamp(datefrom) *1000- (7*60*60 *1000)


def timeLoad_data(datefrom):
    """datefrom = "2024-12-19 13:57:00" convert to int 1734591420000 (- 7 Bangkok) """
    return  dateTime_To_timestamp(datefrom) *1000


########################################################################################################
########################################################################################################
def LoadPrice_Start(req:req_getprice):
    
    """
    https://api.binance.com/api/v3/klines?symbol=XRPUSDT&interval=1m&limit=1
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
    """
    table_collection = req.symbol+'_'+req.tf 
    query = None
    if query is None:
        query = {}
    
    timestamp_min = timeLoadAPI(req.datefrom) if req.datefrom != "" else 0
  
    resp = list(db[table_collection].find().sort("timestamp", -1))
    langthData = len(resp)
    print(langthData)
    #isdata = len(list(db[table_collection].find()))
    isdata = langthData 
    req_lengtbar_ = 10000 if req.limit == 0 else req.limit
    # ถ้า ไม่มี data ให้ Getdata
    if isdata == 0 :
    #if True:
        # Non data
        starttime = 0
        endtime = 0
        lengtbar_ = req_lengtbar_ -1000  if  req_lengtbar_ >= 2000 else req_lengtbar_
        limit_ = 1000
        get_data(req,req.symbol,lengtbar_,limit_,IsUpdate.Empty,starttime ,endtime)
        resp = list(db[table_collection].find())
    else:
        
        # 1. Load Update Price หน้า 
        #   - (ใช้ เวลา Now) - (ราคาจาก Data เวลาล่าสุด)  
        # 2. Load Update Price หลัง
        #   - (ใช้เวลา เก่าสุดใน Data) - (เวลาที่ส่ง Post มา (req.datefrom))
        print('######################################################################################')
        endbar = len(resp)-1
        data_last_time= resp[0]['timestamp'] if len(resp) != 0 else timestamp_min
        data_start_time= resp[endbar]['timestamp'] if len(resp) != 0 else 0

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_timestamp =timeLoadAPI(current_time)
        calbar = 0
        
        """
         lengtbar_ = จำนวนแท่งทั้งหมดที่ Load TF 1m เท่านั้น
         60000 = 60*1000 = 1m
        """
        lengtbar_ = 0
        
        # Update Time
        if current_timestamp > data_last_time:
            calbar = current_timestamp - data_last_time
            if calbar > 60000:
               lengtbar_ = int(calbar/60000)
               print('calbar:',lengtbar_)
        
            limit_ = 1000 if lengtbar_ >= 1000 else lengtbar_
            """ 
                ถ้า get time น้อยกว่า time ที่มีใน data ต้อง Load ใหม่มาเพิ่ม
                starttime = timeต้องLoad <  timeที่มี 
            """
            starttime = data_last_time + (60*1000)
            endtime = 0
            """
            - Load ช่วงเวลาล่าสุดก่อนเสมอ คือ Update Data Price
            - เช็กเวลาที่ Get น้อยกว่า ก็ให้ Load เพิ่ม
            """
            get_data(req,req.symbol,lengtbar_,limit_,IsUpdate.Update,starttime ,endtime)
            
        # Load add Time
        if req.datefrom != "":
            req_strptime_start = timestamp_min

            if req_strptime_start < data_start_time  :
                calbar = data_start_time -req_strptime_start
                if calbar >= 60000:
                    lengtbar_ = int(calbar/60000)

                limit_ = 1000 if lengtbar_ >= 1000 else lengtbar_    
                starttime = data_start_time  
                endtime = data_start_time
                get_data(req,req.symbol,lengtbar_,limit_,IsUpdate.Load,starttime ,endtime)
                
    resp = list(db[table_collection].find().sort("timestamp", -1).limit(req_lengtbar_))            
  
    return resp

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
    """
    .sort("timestamp", 1) น้อย ไป มาก
    .sort("timestamp", -1) มาก ไป น้อย
    Explanation of Operators:
    
        $gt:  A > B
        $lt:  A < B
        $gte: A >= B
        $lte: A <= B
        
        $gt: ตรงกับค่าที่มากกว่าค่าที่ระบุ A > B
            Example: {"timestamp": {"$gt": 1734708600000}} (timestamp > 1734708600000).
        $gte: ตรงกับค่าที่มากกว่าหรือเท่ากับค่าที่ระบุ A >= B
            Example: {"timestamp": {"$gte": 1734708600000}} (timestamp >= 1734708600000).
        $lt: ตรงกับค่าที่ต่ำกว่าค่าที่ระบุ  A < B
            Example: {"timestamp": {"$lt": 1734708700000}} (timestamp < 1734708700000).
        $lte: ตรงกับค่าที่น้อยกว่าหรือเท่ากับค่าที่ระบุ A <= B
            Example: {"timestamp": {"$lte": 1734708700000}} (timestamp <= 1734708700000).
            
        {"timestamp": {"$gte": timestamp_min, "$lte": timestamp_max}}
    """
    timestamp_min = timeLoadAPI(req.datefrom) if req.datefrom != "" else 0
    timestamp_max = timeLoadAPI(req.dateto) if req.dateto != "" else 0
    
    where_Oj = {}
    notWhere = False
    if timestamp_min != 0 and timestamp_max == 0:
        where_Oj = {"timestamp":{"$gte": timestamp_min}}
    if timestamp_max != 0 and timestamp_min == 0:
        where_Oj = {"timestamp":{ "$lte": timestamp_max}}
    if timestamp_max != 0 and timestamp_min != 0:
        where_Oj = {"timestamp":{ "$gte": timestamp_min , "$lte": timestamp_max}}
    if timestamp_max == 0 and timestamp_min == 0:
        notWhere = True
    resp = list(db[table_collection].find(where_Oj).sort("timestamp", -1))
    langthData = len(resp)
    print(langthData)
    isdata = len(list(db[table_collection].find()))
    
    # ถ้า ไม่มี data ให้ Getdata
    if isdata == 0 :
    #if True:
        # Non data
        starttime = 0
        endtime = 0
        lengtbar_ = 1000
        limit_ = 1000
        get_data(req,req.symbol,lengtbar_,limit_,IsUpdate.Empty,starttime ,endtime)
        resp = list(db[table_collection].find())
    else:
        
        # 1. Load Update Price หน้า 
        #   - (ใช้ เวลา Now) - (ราคาจาก Data เวลาล่าสุด)  
        # 2. Load Update Price หลัง
        #   - (ใช้เวลา เก่าสุดใน Data) - (เวลาที่ส่ง Post มา (req.datefrom))
        print('######################################################################################')
        endbar = len(resp)-1
        data_last_time= resp[0]['timestamp'] if len(resp) != 0 else timestamp_min
        data_start_time= resp[endbar]['timestamp'] if len(resp) != 0 else 0
        req_strptime_end = 0 if req.dateto == "" else timestamp_max

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_timestamp =timeLoadAPI(current_time)
        calbar = 0
        """
         lengtbar_ = จำนวนแท่งทั้งหมดที่ Load TF 1m เท่านั้น
         60000 = 60*1000 = 1m
        """
        lengtbar_ = 0
        t = 7*60*60
        # Update Time
        if current_timestamp > data_last_time:
            calbar = current_timestamp - data_last_time
            if calbar > 60000:
               lengtbar_ = int(calbar/60000)
               print('calbar:',lengtbar_)
        
            limit_ = 1000 if lengtbar_ >= 1000 else lengtbar_
            """ 
                ถ้า get time น้อยกว่า time ที่มีใน data ต้อง Load ใหม่มาเพิ่ม
                starttime = timeต้องLoad <  timeที่มี 
            """
            starttime = data_last_time + (60*1000)
            endtime = req_strptime_end
            """
            - Load ช่วงเวลาล่าสุดก่อนเสมอ คือ Update Data Price
            - เช็กเวลาที่ Get น้อยกว่า ก็ให้ Load เพิ่ม
            """
            get_data(req,req.symbol,lengtbar_,limit_,IsUpdate.Update,starttime ,endtime)
            
        # Load add Time
        if req.datefrom != "":
            req_strptime_start = timestamp_min

            if req_strptime_start < data_start_time  :
                calbar = data_start_time -req_strptime_start
                if calbar >= 60000:
                    lengtbar_ = int(calbar/60000)

                limit_ = 1000 if lengtbar_ >= 1000 else lengtbar_    
                starttime = data_start_time  
                endtime = data_start_time
                get_data(req,req.symbol,lengtbar_,limit_,IsUpdate.Load,starttime ,endtime)
                
                
    resp = list(db[table_collection].find().sort("timestamp", -1))            
    #@where_Out = {}
    #@if timestamp_min != 0:
    #@    where_Out = {"timestamp":{ "$gte": timestamp_min , "$lte": timestamp_max}}
    #@if req.getAll:
    #@    resp = list(db[table_collection].find().sort("timestamp", -1))
    #@else:
    #@    if notWhere:
    #@        resp = list(db[table_collection].find().sort("timestamp", -1).limit(1000))
    #@    else:
    #@        
    return resp
   ######################################################################################
   ######################################################################################
   ######################################################################################
   ######################################################################################

def Load_bar_lazy(req:req_getprice):
    """ Load Add bar 1000
    Load Day to Day
    Load Day to Limit
    if Not have bar data set to load from API
    
    Returns:
        _type_: _description_
    """
    table_collection = req.symbol+'_'+req.tf 
    # Output XRPUSDT_1m
    print("table_collection:",table_collection)
    query = None
    if query is None:
        query = {}
    timestamp_min = timeLoadAPI(req.datefrom) if req.datefrom != "" else 0
    timestamp_max = timeLoadAPI(req.dateto) if req.dateto != "" else 0
    """
        $gt:  A > B
        $lt:  A < B
        $gte: A >= B
        $lte: A <= B
    """
    where_Oj = {}
    notWhere = False
    if timestamp_min != 0 and timestamp_max == 0:
        where_Oj = {"timestamp":{"$gte": timestamp_min}}
    if timestamp_max != 0 and timestamp_min == 0:
        where_Oj = {"timestamp":{ "$lte": timestamp_max}}
    if timestamp_max != 0 and timestamp_min != 0:
        where_Oj = {"timestamp":{ "$gte": timestamp_min , "$lte": timestamp_max}}
    if timestamp_max == 0 and timestamp_min == 0:
        notWhere = True
    resp = list(db[table_collection].find(where_Oj).sort("timestamp", -1))
    langthData = len(resp)
    print(langthData)
    if langthData < 999 :
        data = list(db[table_collection].find().sort("timestamp", -1))
        isdata = len(data)
        endbar = isdata-1
        data_start_time= data[endbar]['timestamp'] if isdata != 0 else 0

        # Load add Time
        if req.datefrom != "":
            req_strptime_start = timestamp_min
            if req_strptime_start < data_start_time  :
                calbar = data_start_time -req_strptime_start
                if calbar >= 60000:
                    lengtbar_ = int(calbar/60000)

                limit_ = 1000 if lengtbar_ >= 1000 else lengtbar_    
                starttime = data_start_time  
                endtime = data_start_time
                get_data(req,req.symbol,lengtbar_,limit_,IsUpdate.Load,starttime ,endtime)
                
    resp = list(db[table_collection].find(where_Oj).sort("timestamp", -1))            
    
    return resp


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
        if len(str(lastEndTime)) < 13:
            lastEndTime = ((lastEndTime) * 1000 - utc )
        else:
            lastEndTime = ((lastEndTime) - utc )

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
def load_data(symbol, interval, limit, startTime,endtime):
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
    if endtime != 0 and 1==1:
        params['endTime'] = endtime
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

def get_data(req:req_getprice,symbol_,lengtbar_ ,limit_,isUpdate ,starttime = 0 ,endtime = 0):
    """
        - ถ้า จำนวน lengtbar_ < 1000 จะไม่กระจาย Load จะ Load ทีเดียว  จะ Load โดยใช้ End Time
        - ถ้า จำนวน lengtbar_ > 1000  จะ คำนวนเวลา แล้วกระจาย Load 
        - รอบสุดท้ายที่กระจาย Load จะมีเศษ bar ไม่ถึง 1000 จะ Load โดยใช้ End Time
   
        lengtbar_ = bar ราคาทั้งหมด ที่จะ Load 
        limit_ = จำนวน bar ที่ Load แต่ละรอบ
        num_batches = จำนวน รอบที่ Load
    
    """ 
    num_batches =0
    if lengtbar_ != 0:
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
            x = load_data(symbol_, req.tf, limit_, starttime,endtime)
            data_ALL.extend(x)  # Use extend to add elements of x to data_ALL
            
            if len(x) > 0 :
                st = StartNewTime(interval, limit_)
                startTime = x[0][0] - st
                loadTime.append(startTime)
            # --------------------------------------------------
        else:
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
            if starttime != 0 :
                if isUpdate == 2:
                    loadTime.append(starttime)
                    starttime = 0
                else:
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
        future_to_time = {executor.submit(load_data, symbol_, interval, limit_, time,endtime): time for time in loadTime}
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
    resp = SortData(data_ALL)
    table_collection = req.symbol+'_'+req.tf 
    t = 7*60*60*1000
    print("Number Data:",len(resp))
    print("download Success...")
    print("----------------------------------------------------")
    #for item in resp:
    #    print(convert_timestamp(item[0]+t))
    print("----------------------------------------------------")
    if isUpdate != 4:
        if len(resp) > 0:
            insert(table_collection,resp)
    return resp
    
def deleteData(tableName : str):
    try:
        # Check if the collection exists
        if tableName in db.list_collection_names():
            db[tableName].drop()  # Drop the collection
            return {"status": 200, "message": f"Collection '{tableName}' deleted successfully."}
        else:
            return {"status": 404, "message": f"Collection '{tableName}' not found."}
    except Exception as e:
        return {"status": 500, "message": f"Error occurred: {str(e)}"}