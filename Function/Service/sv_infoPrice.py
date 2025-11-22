
from Function.MongoDatabase import Config
from Function.Models.model_routes_infoPrice import req_getprice,IsUpdate,DeleteRequest
import asyncio
import requests

from datetime import datetime,timedelta,timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

db= Config.connet()

# Bangkok timezone constant
BANGKOK_TIMEZONE = "Asia/Bangkok"
BANGKOK_OFFSET_HOURS = 7
BANGKOK_OFFSET_SECONDS = BANGKOK_OFFSET_HOURS * 60 * 60
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

def convert_to_buddhist_year(ad_year: int) -> int:
    """
    Convert AD (Christian Era) year to BE (Buddhist Era) year
    
    Args:
        ad_year (int): Year in AD (Christian Era)
    
    Returns:
        int: Year in BE (Buddhist Era)
    """
    return ad_year + 543

def convert_timestamp(timestamp:int, use_buddhist_year: bool = True):
    """convert timestamp to datetime string

    Args:
        timestamp (int): 1734591480000
        use_buddhist_year (bool): If True, use Buddhist Era (BE) year, else use AD year. Default: True

    Returns:
        str : 19/12/2567 6:58:00 (if use_buddhist_year=True)
              or 2024-12-19 06:58:00 (if use_buddhist_year=False)
    """
    # Convert milliseconds to seconds
    timestamp_sec = timestamp / 1000
    # Convert to datetime
    date_time = datetime.utcfromtimestamp(timestamp_sec)
    
    if use_buddhist_year:
        # Convert to Buddhist Era (BE) year
        be_year = convert_to_buddhist_year(date_time.year)
        # Format with Buddhist year: DD/MM/BE HH:MM:SS
        return date_time.strftime(f"%d/%m/{be_year} %H:%M:%S")
    else:
        # Format datetime as string (AD year)
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

def validate_timezone(timezone_str: str) -> bool:
    """
    Validate if the timezone is Bangkok timezone (Asia/Bangkok)
    
    Args:
        timezone_str (str): Timezone string from client (e.g., "Asia/Bangkok")
    
    Returns:
        bool: True if timezone is Bangkok, False otherwise
    """
    try:
        # Check if timezone matches Bangkok exactly
        if timezone_str == BANGKOK_TIMEZONE:
            return True
        
        # Also check for common variations
        bangkok_variations = ["Asia/Bangkok", "Bangkok", "UTC+7", "+07:00", "ICT", "Indochina Time"]
        if timezone_str in bangkok_variations:
            return True
        
        # Check if timezone string contains Bangkok or UTC+7
        timezone_lower = timezone_str.lower()
        if "bangkok" in timezone_lower or "utc+7" in timezone_lower or "+07:00" in timezone_str:
            return True
        
        # Try to use zoneinfo (Python 3.9+) if available, otherwise skip
        try:
            from zoneinfo import ZoneInfo
            tz = ZoneInfo(timezone_str)
            now = datetime.now(tz)
            offset = now.utcoffset().total_seconds() / 3600
            if offset == BANGKOK_OFFSET_HOURS:
                return True
        except (ImportError, Exception):
            # zoneinfo not available or timezone invalid, skip
            pass
        
        return False
    except Exception as e:
        print(f"WARNING: validate_timezone error: {e}")
        return False

def log_timezone_info(req: req_getprice):
    """
    Log timezone information for debugging
    
    Args:
        req: Request object with timezone field
    """
    timezone_valid = validate_timezone(req.timezone)
    print("=" * 80)
    print(f"TIMEZONE CHECK:")
    print(f"  Client timezone: {req.timezone}")
    print(f"  Expected timezone: {BANGKOK_TIMEZONE} (UTC+7)")
    print(f"  Timezone valid: {timezone_valid}")
    if not timezone_valid:
        print(f"  WARNING: Client timezone ({req.timezone}) does not match expected Bangkok timezone!")
        print(f"  Backend will use Bangkok timezone (UTC+7) for calculations.")
    print("=" * 80)

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
    # Validate and log timezone information
    log_timezone_info(req)
    
    table_collection = req.symbol+'_'+req.tf 
    query = None
    if query is None:
        query = {}
    
    timestamp_min = timeLoadAPI(req.datefrom) if req.datefrom != "" else 0
    resp = list(db[table_collection].find().sort("timestamp", -1))
    langthData = len(resp)
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
    
    # Check data continuity after loading
    if len(resp) > 0:
        continuity_result = check_data_continuity(table_collection, req.tf, limit=min(500, len(resp)))
        if continuity_result.get('gaps_found', 0) > 0:
            print(f"⚠️  WARNING: Found {continuity_result.get('gaps_found')} gaps in loaded data")
        else:
            print(f"✅ Loaded data continuity verified: {len(resp)} records")
  
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
    # Validate and log timezone information
    log_timezone_info(req)
   
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
    
    # Check data continuity after loading
    if len(resp) > 0:
        continuity_result = check_data_continuity(table_collection, req.tf, limit=min(1000, len(resp)))
        if continuity_result.get('gaps_found', 0) > 0:
            print(f"⚠️  WARNING: Found {continuity_result.get('gaps_found')} gaps in {table_collection}")
            print(f"   Missing {continuity_result.get('missing_bars_total', 0)} bars total")
        else:
            print(f"✅ Data continuity verified: {len(resp)} records are continuous")
    
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
    # Validate and log timezone information
    log_timezone_info(req)
    
    table_collection = req.symbol+'_'+req.tf 
    # Output XRPUSDT_1m
    print("=" * 80)
    print(f"DEBUG: Load_bar_lazy - table_collection: {table_collection}")
    
    # Calculate interval milliseconds based on req.tf
    interval_units = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
        'w': 604800
    }
    interval_value = int(req.tf[:-1])
    interval_unit = req.tf[-1]
    interval_ms = interval_value * interval_units[interval_unit] * 1000
    print(f"DEBUG: Load_bar_lazy - interval_ms: {interval_ms} (from tf: {req.tf})")
    
    timestamp_min = timeLoadAPI(req.datefrom) if req.datefrom != "" else 0
    timestamp_max = timeLoadAPI(req.dateto) if req.dateto != "" else 0
    
    print(f"DEBUG: Load_bar_lazy - timestamp_min: {timestamp_min} ({convert_timestamp(timestamp_min) if timestamp_min > 0 else 'N/A'})")
    print(f"DEBUG: Load_bar_lazy - timestamp_max: {timestamp_max} ({convert_timestamp(timestamp_max) if timestamp_max > 0 else 'N/A'})")
    
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
    
    print(f"DEBUG: Load_bar_lazy - where_Oj: {where_Oj}")
    
    resp = list(db[table_collection].find(where_Oj).sort("timestamp", -1))
    langthData = len(resp)
    print(f"DEBUG: Load_bar_lazy - langthData (filtered): {langthData}")
    
    if langthData < 999:
        print("DEBUG: Load_bar_lazy - langthData < 999, loading additional data...")
        data = list(db[table_collection].find().sort("timestamp", -1))
        isdata = len(data)
        print(f"DEBUG: Load_bar_lazy - isdata (total in DB): {isdata}")
        
        endbar = isdata-1
        data_start_time = data[endbar]['timestamp'] if isdata != 0 else 0
        data_last_time = data[0]['timestamp'] if isdata != 0 else 0
        
        print(f"DEBUG: Load_bar_lazy - data_start_time (oldest): {data_start_time} ({convert_timestamp(data_start_time) if data_start_time > 0 else 'N/A'})")
        print(f"DEBUG: Load_bar_lazy - data_last_time (newest): {data_last_time} ({convert_timestamp(data_last_time) if data_last_time > 0 else 'N/A'})")

        # Load add Time
        if req.datefrom != "":
            req_strptime_start = timestamp_min
            print(f"DEBUG: Load_bar_lazy - req_strptime_start: {req_strptime_start} ({convert_timestamp(req_strptime_start) if req_strptime_start > 0 else 'N/A'})")
            
            if req_strptime_start < data_start_time:
                calbar = data_start_time - req_strptime_start
                print(f"DEBUG: Load_bar_lazy - calbar (time difference): {calbar} ms")
                
                if calbar >= interval_ms:
                    lengtbar_ = int(calbar / interval_ms)
                    print(f"DEBUG: Load_bar_lazy - lengtbar_ (bars to load): {lengtbar_}")
                    
                    limit_ = 1000 if lengtbar_ >= 1000 else lengtbar_
                    # We need to load from req_strptime_start to data_start_time
                    # For Load mode, we need to load backwards from data_start_time
                    # The issue is that we need to load data BEFORE data_start_time
                    # So we calculate: we want to load from req_strptime_start to data_start_time
                    # In get_data, for Load mode, it calculates: starttime - (limit_ * interval_ms)
                    # So if we set starttime = data_start_time, it will calculate: data_start_time - (limit_ * interval_ms)
                    # But we need to ensure that the calculated time is >= req_strptime_start
                    # Actually, we should set starttime to req_strptime_start + (limit_ * interval_ms)
                    # so that when get_data subtracts, we get req_strptime_start
                    st = StartNewTime(req.tf, limit_)
                    starttime = req_strptime_start + st  # This will be adjusted in get_data
                    endtime = req_strptime_start  # Earliest time we need (for filtering)
                    
                    print(f"DEBUG: Load_bar_lazy - Loading data:")
                    print(f"  lengtbar_: {lengtbar_}")
                    print(f"  limit_: {limit_}")
                    print(f"  starttime (before adjustment): {starttime} ({convert_timestamp(starttime) if starttime > 0 else 'N/A'})")
                    print(f"  endtime: {endtime} ({convert_timestamp(endtime) if endtime > 0 else 'N/A'})")
                    print(f"  Time range: {calbar} ms = {calbar/interval_ms:.2f} bars")
                    print(f"  Will load from {convert_timestamp(endtime)} to {convert_timestamp(data_start_time)}")
                    
                    get_data(req, req.symbol, lengtbar_, limit_, IsUpdate.Load, starttime, endtime, data_start_time)
                else:
                    print(f"DEBUG: Load_bar_lazy - calbar < interval_ms, skipping load")
            else:
                print(f"DEBUG: Load_bar_lazy - req_strptime_start >= data_start_time, no need to load older data")
        else:
            print(f"DEBUG: Load_bar_lazy - req.datefrom is empty, skipping load")
                
    resp = list(db[table_collection].find(where_Oj).sort("timestamp", -1))
    print(f"DEBUG: Load_bar_lazy - Final resp length: {len(resp)}")
    
    # Check data continuity before returning
    if len(resp) > 0:
        continuity_result = check_data_continuity(table_collection, req.tf, limit=min(1000, len(resp)))
        if continuity_result.get('gaps_found', 0) > 0:
            print(f"⚠️  WARNING: Found {continuity_result.get('gaps_found')} gaps in {table_collection}")
            print(f"   Missing {continuity_result.get('missing_bars_total', 0)} bars total")
        else:
            print(f"✅ Data continuity verified: {len(resp)} records are continuous")
    
    print("=" * 80)
    
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
    
    if limit > 0:
        params['limit'] = limit
        
    if startTime != 0:
        params['startTime'] = startTime
    if endtime != 0:
        params['endTime'] = endtime
    
    print(f"DEBUG: load_data - API params: {params}")
    print(f"DEBUG: load_data - startTime: {startTime} ({convert_timestamp(startTime) if startTime > 0 else 'N/A'})")
    print(f"DEBUG: load_data - endtime: {endtime} ({convert_timestamp(endtime) if endtime > 0 else 'N/A'})")
    
    response = requests.get(base_url, params=params)
    data = []
    if response.status_code == 200:
        data = response.json()
        print(f"DEBUG: load_data - API returned {len(data)} items")
        if len(data) > 0:
            print(f"DEBUG: load_data - First item timestamp: {data[0][0]} ({convert_timestamp(data[0][0])})")
            print(f"DEBUG: load_data - Last item timestamp: {data[-1][0]} ({convert_timestamp(data[-1][0])})")
    else:
        print(f"ERROR: load_data - API returned status {response.status_code}: {response.text}")
    
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

def check_data_continuity(table_collection: str, interval_tf: str, limit: int = 100):
    """
    Check data continuity in database to ensure no gaps between timestamps.
    
    Args:
        table_collection (str): MongoDB collection name (e.g., 'BTCUSDT_1h')
        interval_tf (str): Timeframe interval (e.g., '1h', '1m', '5m')
        limit (int): Number of recent records to check (default: 100)
    
    Returns:
        dict: Continuity check results with gaps information
    """
    try:
        # Get recent data sorted by timestamp
        recent_data = list(db[table_collection].find().sort("timestamp", -1).limit(limit))
        
        if len(recent_data) < 2:
            return {
                "status": "insufficient_data",
                "message": f"Not enough data to check continuity (found {len(recent_data)} records)",
                "gaps": [],
                "total_records": len(recent_data)
            }
        
        # Calculate interval milliseconds
        interval_units = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
            'w': 604800
        }
        interval_value = int(interval_tf[:-1])
        interval_unit = interval_tf[-1]
        expected_interval_ms = interval_value * interval_units[interval_unit] * 1000
        
        # Sort by timestamp ascending for gap detection
        sorted_data = sorted(recent_data, key=lambda x: x['timestamp'])
        
        gaps = []
        missing_count = 0
        
        for i in range(1, len(sorted_data)):
            prev_timestamp = sorted_data[i-1]['timestamp']
            curr_timestamp = sorted_data[i]['timestamp']
            actual_gap = curr_timestamp - prev_timestamp
            
            if actual_gap != expected_interval_ms:
                missing_bars = int((actual_gap - expected_interval_ms) / expected_interval_ms)
                gaps.append({
                    "index": i,
                    "prev_timestamp": prev_timestamp,
                    "prev_time": convert_timestamp(prev_timestamp),
                    "curr_timestamp": curr_timestamp,
                    "curr_time": convert_timestamp(curr_timestamp),
                    "expected_gap_ms": expected_interval_ms,
                    "actual_gap_ms": actual_gap,
                    "missing_bars": missing_bars,
                    "gap_duration_minutes": (actual_gap - expected_interval_ms) / (60 * 1000)
                })
                missing_count += missing_bars
        
        return {
            "status": "checked",
            "total_records": len(recent_data),
            "checked_records": len(sorted_data),
            "expected_interval_ms": expected_interval_ms,
            "gaps_found": len(gaps),
            "missing_bars_total": missing_count,
            "gaps": gaps[:10],  # Return first 10 gaps
            "is_continuous": len(gaps) == 0
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking continuity: {str(e)}",
            "gaps": []
        }

def log_continuity_check(table_collection: str, interval_tf: str):
    """
    Log continuity check results for debugging.
    
    Args:
        table_collection (str): MongoDB collection name
        interval_tf (str): Timeframe interval
    """
    continuity_result = check_data_continuity(table_collection, interval_tf, limit=1000)
    
    print("=" * 80)
    print(f"CONTINUITY CHECK: {table_collection}")
    print(f"  Status: {continuity_result.get('status')}")
    print(f"  Total records checked: {continuity_result.get('checked_records', 0)}")
    print(f"  Expected interval: {continuity_result.get('expected_interval_ms', 0)} ms")
    
    if continuity_result.get('gaps_found', 0) > 0:
        print(f"  ⚠️  GAPS FOUND: {continuity_result.get('gaps_found')} gaps")
        print(f"  ⚠️  Missing bars: {continuity_result.get('missing_bars_total', 0)} bars")
        print(f"  First few gaps:")
        for gap in continuity_result.get('gaps', [])[:5]:
            print(f"    - Gap at index {gap['index']}:")
            print(f"      From: {gap['prev_time']} ({gap['prev_timestamp']})")
            print(f"      To: {gap['curr_time']} ({gap['curr_timestamp']})")
            print(f"      Missing: {gap['missing_bars']} bars ({gap['gap_duration_minutes']:.1f} minutes)")
    else:
        print(f"  ✅ Data is continuous - no gaps found")
    
    print("=" * 80)
    
    return continuity_result

def insert(table_collection, data, update_existing: bool = False):
    """
    Insert data into the specified MongoDB collection.
    Prevents duplicate insertion by checking existing timestamps.
    Optionally updates existing records if update_existing is True.

    Parameters:
        table_collection (str): The name of the MongoDB collection.
        data (list of lists): A list of rows, where each row is a list of values.
        update_existing (bool): If True, update existing records instead of skipping them. Default: False.

    Returns:
        dict: Result containing insert_count, update_count, and skipped_count
    """
    if len(data) == 0:
        return {"insert_count": 0, "update_count": 0, "skipped_count": 0}
    
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
    
    # Check for existing timestamps
    timestamps = [item["timestamp"] for item in ojData]
    existing_timestamps = set(db[table_collection].find({"timestamp": {"$in": timestamps}}, {"timestamp": 1}).distinct("timestamp"))
    
    # Separate new data and existing data
    new_data = [item for item in ojData if item["timestamp"] not in existing_timestamps]
    existing_data = [item for item in ojData if item["timestamp"] in existing_timestamps]
    
    insert_count = 0
    update_count = 0
    skipped_count = 0
    
    # Insert new data
    if len(new_data) > 0:
        if len(new_data) == 1:
            result = db[table_collection].insert_one(new_data[0])
            insert_count = 1 if result.inserted_id else 0
        else:
            result = db[table_collection].insert_many(new_data)
            insert_count = len(result.inserted_ids) if result.inserted_ids else 0
        print(f"DEBUG: insert - Inserted {insert_count} new items into {table_collection}")
    
    # Update existing data if update_existing is True
    if len(existing_data) > 0:
        if update_existing:
            for item in existing_data:
                # Update existing document, preserving Create_Date if it exists
                update_result = db[table_collection].update_one(
                    {"timestamp": item["timestamp"]},
                    {
                        "$set": {
                            "open": item["open"],
                            "high": item["high"],
                            "low": item["low"],
                            "close": item["close"],
                            "volume": item["volume"],
                            "Update_Date": current_time,  # Add update date
                        }
                    }
                )
                if update_result.modified_count > 0:
                    update_count += 1
            print(f"DEBUG: insert - Updated {update_count} existing items in {table_collection}")
        else:
            skipped_count = len(existing_data)
            print(f"DEBUG: insert - Skipped {skipped_count} existing items in {table_collection} (update_existing=False)")
    
    # Summary
    total_processed = insert_count + update_count + skipped_count
    if total_processed > 0:
        print(f"DEBUG: insert - Summary: {insert_count} inserted, {update_count} updated, {skipped_count} skipped (total: {total_processed})")
    
    if insert_count == 0 and update_count == 0 and skipped_count == len(ojData):
        print(f"DEBUG: insert - All {len(ojData)} items already exist in {table_collection}, no updates performed")
    
    return {
        "insert_count": insert_count,
        "update_count": update_count,
        "skipped_count": skipped_count,
        "total_processed": total_processed
    }
########################################################################################################
########################################################################################################

def get_data(req:req_getprice,symbol_,lengtbar_ ,limit_,isUpdate ,starttime = 0 ,endtime = 0, original_starttime = 0):
    """
        - ถ้า จำนวน lengtbar_ < 1000 จะไม่กระจาย Load จะ Load ทีเดียว  จะ Load โดยใช้ End Time
        - ถ้า จำนวน lengtbar_ > 1000  จะ คำนวนเวลา แล้วกระจาย Load 
        - รอบสุดท้ายที่กระจาย Load จะมีเศษ bar ไม่ถึง 1000 จะ Load โดยใช้ End Time
   
        lengtbar_ = bar ราคาทั้งหมด ที่จะ Load 
        limit_ = จำนวน bar ที่ Load แต่ละรอบ
        num_batches = จำนวน รอบที่ Load
    
    """ 
    try:
        print("=" * 80)
        print(f"DEBUG: get_data - symbol_: {symbol_}, tf: {req.tf}, lengtbar_: {lengtbar_}, limit_: {limit_}")
        print(f"DEBUG: get_data - isUpdate: {isUpdate}, starttime: {starttime}, endtime: {endtime}")
        print(f"DEBUG: get_data - starttime: {convert_timestamp(starttime) if starttime > 0 else 'N/A'}")
        print(f"DEBUG: get_data - endtime: {convert_timestamp(endtime) if endtime > 0 else 'N/A'}")
        
        # Use req.tf instead of global interval
        interval_tf = req.tf
        
        num_batches = 0
        if lengtbar_ != 0:
            num_batches = int(lengtbar_ / limit_)
            # If there's a remainder, we need one more batch
            if lengtbar_ % limit_ != 0:
                num_batches += 1
        data_ALL = []
        print("download.....")
        loadTime= []
        if lengtbar_ > 0 and num_batches == 0:
            num_batches = 1

        print(f"DEBUG: get_data - num_batches: {num_batches} (lengtbar_: {lengtbar_}, limit_: {limit_})")

        # หาค่า เวลา แล้วกระจาย Load
        for _ in range(num_batches):

            if _ == 0 and starttime == 0:
                # --------------------------------------------------
                # First batch: load latest data without startTime
                x = load_data(symbol_, interval_tf, limit_, starttime, endtime)
                data_ALL.extend(x)  # Use extend to add elements of x to data_ALL
                print(f"DEBUG: get_data - First batch loaded {len(x)} items")

                if len(x) > 0:
                    # Only calculate next startTime if we have more batches to load
                    if num_batches > 1:
                        # Calculate the next startTime for loading older data
                        # We want to load data BEFORE the first item we just got
                        # So we use the first item's timestamp minus one interval
                        st = StartNewTime(interval_tf, 1)  # One interval, not limit_
                        startTime = x[0][0] - st
                        loadTime.append(startTime)
                        print(f"DEBUG: get_data - First batch startTime for next batch: {startTime} ({convert_timestamp(startTime) if startTime > 0 else 'N/A'})")
                    print(f"DEBUG: get_data - First batch first timestamp: {x[0][0]} ({convert_timestamp(x[0][0])})")
                    print(f"DEBUG: get_data - First batch last timestamp: {x[-1][0]} ({convert_timestamp(x[-1][0])})")
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
                if starttime != 0:
                    if isUpdate == 2:  # Update mode - use starttime directly
                        loadTime.append(starttime)
                        print(f"DEBUG: get_data - Batch {_}: Using starttime directly (Update mode): {starttime}")
                        starttime = 0
                    elif isUpdate == 3:  # Load mode - load from starttime backwards to endtime
                        # For Load mode, we want to load from starttime going backwards to endtime
                        # starttime is already set to req_strptime_start + (limit_ * interval_ms) in Load_bar_lazy
                        # So when we use it as startTime for API, we need to ensure startTime < endTime
                        # Actually, we should use starttime directly, but we need to ensure it's < endtime
                        # Wait, for Binance API, startTime should be < endTime
                        # But we're loading backwards, so we want to load from endtime to starttime
                        # So we should use endtime as startTime and starttime as endTime
                        if len(str(starttime)) < 13:
                            starttime = starttime * 1000
                        if len(str(endtime)) < 13 and endtime > 0:
                            endtime = endtime * 1000
                        
                        # For Load mode, we want to load from endtime (earliest) to starttime (latest)
                        # But Binance API requires startTime < endTime
                        # So we use endtime as startTime and starttime as endTime
                        if endtime > 0 and starttime > endtime:
                            # Use endtime as startTime (earliest time we need)
                            loadTime.append(endtime)
                            print(f"DEBUG: get_data - Batch {_}: Load mode - Using endtime as startTime: {endtime} ({convert_timestamp(endtime) if endtime > 0 else 'N/A'})")
                            print(f"DEBUG: get_data - Batch {_}: Load mode - Will use starttime as endTime: {starttime} ({convert_timestamp(starttime) if starttime > 0 else 'N/A'})")
                        else:
                            # Fallback: use starttime directly
                            loadTime.append(starttime)
                            print(f"DEBUG: get_data - Batch {_}: Load mode - Using starttime: {starttime} ({convert_timestamp(starttime) if starttime > 0 else 'N/A'})")
                        starttime = 0
                    else:  # Other modes
                        st = StartNewTime(interval_tf, limit_)
                        if len(str(starttime)) < 13:
                            starttime = starttime * 1000
                        calculated_time = starttime - st
                        loadTime.append(calculated_time)
                        print(f"DEBUG: get_data - Batch {_}: Calculated time: {calculated_time} ({convert_timestamp(calculated_time) if calculated_time > 0 else 'N/A'})")
                        starttime = 0
                else:
                    # Continue loading from the previous batch
                    if isUpdate == 3:  # Load mode - load forward from last timestamp
                        # In Load mode, we load forward from the last timestamp of previous batch
                        # We need to continue from where batch 0 ended
                        # The issue: Binance API returns data up to (but not including) endTime
                        # So if batch 0 uses endTime=1763735640000 (14:34:00), it returns data up to 14:33:00
                        # But actually it returns up to 14:32:00 (last item timestamp)
                        # This means we need to start batch 1 from 14:33:00 (14:32:00 + 1 interval)
                        last_startTime = loadTime[len(loadTime)-1]
                        # Calculate the theoretical end time of previous batch: last_startTime + (limit_ * interval_ms)
                        last_batch_duration = StartNewTime(interval_tf, limit_)
                        last_batch_endTime = last_startTime + last_batch_duration
                        # But Binance API may not return data exactly up to endTime
                        # So we should start batch 1 from last_batch_endTime (which is where batch 0 should theoretically end)
                        # This ensures continuity: batch 0 ends at 14:33:00, batch 1 starts at 14:33:00
                        startTime = last_batch_endTime
                        # Check if we've reached or exceeded original_starttime (data_start_time)
                        if original_starttime > 0 and startTime >= original_starttime:
                            # We've reached the latest time we need, stop here
                            print(f"DEBUG: get_data - Batch {_}: Reached original_starttime ({convert_timestamp(original_starttime)}), stopping batch generation")
                            break
                        loadTime.append(startTime)
                        print(f"DEBUG: get_data - Batch {_}: Load mode - Calculated forward from previous batch end: {startTime} ({convert_timestamp(startTime) if startTime > 0 else 'N/A'})")
                        print(f"DEBUG: get_data - Batch {_}: Previous batch theoretical end: {last_batch_endTime} ({convert_timestamp(last_batch_endTime) if last_batch_endTime > 0 else 'N/A'})")
                    else:
                        # Other modes: continue loading backwards
                        st = StartNewTime(interval_tf, limit_)
                        startTime = loadTime[len(loadTime)-1] - st
                        loadTime.append(startTime)
                        print(f"DEBUG: get_data - Batch {_}: Calculated from previous: {startTime} ({convert_timestamp(startTime) if startTime > 0 else 'N/A'})")

        print(f"DEBUG: get_data - loadTime array: {loadTime}")
        print(f"DEBUG: get_data - loadTime count: {len(loadTime)}")

        # Create Task Get API Multi Task max_workers:20 

        with ThreadPoolExecutor(max_workers=20) as executor:
            # For Load mode, we need to use endtime to limit the range
            future_to_time = {}
            for idx, time in enumerate(loadTime):
                # For Load mode, use original_starttime (data_start_time) as endTime parameter for API
                if isUpdate == 3 and original_starttime > 0:
                    # For the last batch, use original_starttime as endTime
                    # For other batches, use the next batch's startTime as endTime (or original_starttime if it's the last)
                    if idx == len(loadTime) - 1:
                        # Last batch: use original_starttime
                        api_endtime = original_starttime
                    else:
                        # Not last batch: use next batch's startTime as endTime
                        # For Load mode, we want continuous data
                        # Binance API returns data up to (but not including) endTime
                        # So if batch 0 uses endTime = batch 1's startTime (14:34:00), it returns data up to 14:33:00
                        # But we want batch 0 to return data up to 14:33:00, so batch 1 can start from 14:33:00
                        # So we should use next batch's startTime as endTime directly
                        api_endtime = loadTime[idx + 1]
                else:
                    api_endtime = endtime
                
                # Ensure startTime < endTime for Binance API
                if api_endtime > 0 and time >= api_endtime:
                    print(f"WARNING: get_data - startTime >= endTime for batch {idx}, adjusting...")
                    # Adjust: use time as endTime and calculate new startTime
                    st = StartNewTime(interval_tf, limit_)
                    adjusted_starttime = time - st
                    if adjusted_starttime > 0:
                        time = adjusted_starttime
                        print(f"DEBUG: get_data - Adjusted startTime to: {time} ({convert_timestamp(time) if time > 0 else 'N/A'})")
                
                future = executor.submit(load_data, symbol_, interval_tf, limit_, time, api_endtime)
                future_to_time[future] = time
                print(f"DEBUG: get_data - Submitting request batch {idx}: startTime={time} ({convert_timestamp(time) if time > 0 else 'N/A'}), endTime={api_endtime} ({convert_timestamp(api_endtime) if api_endtime > 0 else 'N/A'})")
            
            for future in as_completed(future_to_time):
                time = future_to_time[future]
                try:
                    data = future.result()
                    print(f"DEBUG: get_data - API returned {len(data)} items for time {time}")
                    
                    # Filter data to ensure it's within the required range for Load mode
                    if isUpdate == 3 and endtime > 0:
                        # Only include data that is >= endtime (req_strptime_start) and <= data_start_time
                        filtered_data = [item for item in data if item[0] >= endtime]
                        data_ALL.extend(filtered_data)
                        if len(filtered_data) < len(data):
                            print(f"DEBUG: get_data - Filtered {len(data) - len(filtered_data)} items outside range (endtime: {endtime})")
                        print(f"DEBUG: get_data - Added {len(filtered_data)} items (from {len(data)} total) for time {time}")
                    else:
                        data_ALL.extend(data)
                        print(f"DEBUG: get_data - Added {len(data)} items for time {time}")
                except Exception as e:
                    print(f"ERROR: get_data - Request failed for time {time}: {e}")
                    import traceback
                    traceback.print_exc()
    
        resp = SortData(data_ALL)
        table_collection = req.symbol+'_'+req.tf 
        t = 7*60*60*1000
        
        print(f"DEBUG: get_data - Total data loaded (before deduplication): {len(resp)}")
        
        # Remove duplicates based on timestamp
        if len(resp) > 0:
            seen_timestamps = set()
            unique_resp = []
            duplicates_count = 0
            
            for item in resp:
                ts = item[0]
                if ts not in seen_timestamps:
                    unique_resp.append(item)
                    seen_timestamps.add(ts)
                else:
                    duplicates_count += 1
            
            if duplicates_count > 0:
                print(f"WARNING: get_data - Found {duplicates_count} duplicate timestamps, removing them")
            
            resp = unique_resp
            print(f"DEBUG: get_data - Total data after deduplication: {len(resp)}")
            
            if len(resp) > 0:
                print(f"DEBUG: get_data - First timestamp: {resp[0][0]} ({convert_timestamp(resp[0][0])})")
                print(f"DEBUG: get_data - Last timestamp: {resp[-1][0]} ({convert_timestamp(resp[-1][0])})")
                
                # Check for gaps
                if len(resp) > 1:
                    gaps_found = []
                    for i in range(1, min(20, len(resp))):  # Check first 20 items
                        gap = resp[i][0] - resp[i-1][0]
                        expected_gap = StartNewTime(interval_tf, 1)
                        if gap != expected_gap:
                            gaps_found.append((i, gap, expected_gap))
                    
                    if gaps_found:
                        print(f"WARNING: get_data - Found {len(gaps_found)} gaps in first 20 items:")
                        for idx, gap, expected in gaps_found[:5]:  # Show first 5 gaps
                            print(f"  Index {idx}: {gap} ms (expected: {expected} ms)")
        
        print("download Success...")
        print("=" * 80)
        
        if isUpdate != 4:
            if len(resp) > 0:
                # For Update mode (isUpdate == 2), update existing records
                # For other modes, only insert new records
                update_existing = (isUpdate == IsUpdate.Update)
                insert_result = insert(table_collection, resp, update_existing=update_existing)
                
                if insert_result:
                    total = insert_result.get("total_processed", 0)
                    inserted = insert_result.get("insert_count", 0)
                    updated = insert_result.get("update_count", 0)
                    skipped = insert_result.get("skipped_count", 0)
                    
                    if update_existing:
                        print(f"DEBUG: get_data - Update mode: {inserted} inserted, {updated} updated, {skipped} skipped")
                    else:
                        print(f"DEBUG: get_data - Insert mode: {inserted} inserted, {skipped} skipped")
                
                # Check data continuity after insertion (only for significant updates)
                if len(resp) >= 100 or isUpdate == IsUpdate.Update:
                    log_continuity_check(table_collection, req.tf)
        return resp
    except Exception as e:
        print(f"ERROR: Function\Service\sv_infoPrice.py get_data {e}")
        import traceback
        traceback.print_exc()
        raise
    
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