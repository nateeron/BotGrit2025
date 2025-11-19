# BotGrid 2025 - FastAPI Trading Bot

## 📋 ภาพรวมโปรเจกต์

BotGrid 2025 เป็นระบบ Trading Bot ที่ใช้ FastAPI สำหรับการซื้อขายอัตโนมัติบน Binance โดยใช้กลยุทธ์ Grid Trading และมีการเชื่อมต่อ WebSocket เพื่อรับข้อมูลราคาแบบ Real-time

## ✨ คุณสมบัติหลัก

- 🤖 **Trading Bot อัตโนมัติ**: ระบบซื้อขายอัตโนมัติด้วยกลยุทธ์ Grid Trading
- 📊 **Real-time Price Updates**: รับข้อมูลราคาแบบ Real-time ผ่าน WebSocket จาก Binance
- 💰 **Binance Integration**: เชื่อมต่อกับ Binance API สำหรับการซื้อขาย
- 📈 **Backtest System**: ระบบทดสอบกลยุทธ์ด้วยข้อมูลย้อนหลัง
- 🗄️ **MongoDB Storage**: เก็บข้อมูลราคาและคำสั่งซื้อขายใน MongoDB
- ⚙️ **Configuration Management**: จัดการการตั้งค่าผ่าน API

## 🚀 การติดตั้ง

### ความต้องการของระบบ

- Python 3.11 หรือสูงกว่า
- MongoDB
- Binance API Key และ Secret Key

### ขั้นตอนการติดตั้ง

1. **Clone หรือดาวน์โหลดโปรเจกต์**
```bash
cd BotGrit2025
```

2. **ติดตั้ง Dependencies**
```bash
pip install -r requirements.txt
```

3. **ตั้งค่า Configuration**

สร้างไฟล์ `Setting.js` ในโฟลเดอร์หลักของโปรเจกต์:

```javascript
var data = {
    "Connetion": {
        "DATA_HOST": "localhost",
        "DATA_PORT": "27017",
        "DATA_NAME": "BotGrid2025",
        "DATA_USER": "",
        "DATA_PASSWORD": ""
    }
}
```

4. **ตั้งค่า Binance API**

แก้ไขไฟล์ `Function/MongoDatabase.py` และเพิ่ม API Key และ Secret Key ของคุณ:

```python
ConnetBinace = {
    "API_KEY": "YOUR_API_KEY",
    "API_SECRET": "YOUR_SECRET_KEY",
    "LINE_ADMIN": "YOUR_LINE_TOKEN",
    "LINE_ADMIN2": "YOUR_LINE_TOKEN_2"
}
```

## 🏃 การรันโปรแกรม

### รันเซิร์ฟเวอร์ FastAPI

```bash
python FastAPI_BotGrid2025.py
```

เซิร์ฟเวอร์จะรันที่: **http://localhost:45441**

### ตรวจสอบว่าเซิร์ฟเวอร์ทำงาน

เปิดเบราว์เซอร์ไปที่:
- http://localhost:45441/docs - Swagger UI สำหรับทดสอบ API
- http://localhost:45441/redoc - ReDoc สำหรับดูเอกสาร API

## 📚 โครงสร้างโปรเจกต์

```
BotGrit2025/
├── FastAPI_BotGrid2025.py      # ไฟล์หลักของ FastAPI Application
├── requirements.txt             # Dependencies
├── Setting.js                   # ไฟล์ตั้งค่า MongoDB
├── Dockerfile                   # Docker configuration
│
├── Function/
│   ├── Models/                  # Pydantic Models สำหรับ Request/Response
│   │   ├── model_routes_botGrid.py
│   │   ├── model_routes_ConfigBot.py
│   │   ├── model_routes_infoPrice.py
│   │   └── models.py
│   │
│   ├── Routes/                  # API Routes
│   │   ├── routes.py            # Routes หลัก
│   │   ├── routes_BotGrid.py    # Routes สำหรับ BotGrid
│   │   ├── routes_ConfigBot.py  # Routes สำหรับ Configuration
│   │   └── routes_infoPrice.py  # Routes สำหรับข้อมูลราคา
│   │
│   ├── Service/                 # Business Logic
│   │   ├── sv_botgrid.py        # BotGrid Service
│   │   ├── sv_botgrid_Backtest1_3.py  # Backtest Service
│   │   ├── sv_infoPrice.py      # Price Information Service
│   │   ├── BotGrit_CheckPrice_Fast_API_FN_buy.py  # Price Check & Buy Logic
│   │   ├── BotSpot.py           # Spot Trading Service
│   │   ├── FN_calAction.py      # Action Calculation
│   │   ├── ConvertTime.py       # Time Conversion Utilities
│   │   └── crud.py              # Database CRUD Operations
│   │
│   └── MongoDatabase.py         # MongoDB Connection
│
└── Note_Test/                   # ไฟล์ทดสอบและ UI
    ├── app.py
    └── test UI/
```

## 🔌 API Endpoints

### 1. Health Check & Basic Routes

#### `GET /`
ตรวจสอบว่าเซิร์ฟเวอร์ทำงาน
```json
{
  "message": "OK RUNNING"
}
```

#### `POST /createTable`
สร้าง Collections ใน MongoDB
- `XRPUSDT_1m`
- `BNBUSDT_1m`
- `OrderBuy`
- `ConfigBot`

---

### 2. BotGrid Routes (`/botgrid/*`)

#### `GET /botgrid/run`
ตรวจสอบว่า BotGrid module ทำงาน
```json
{
  "message": "OK RUNNING Botgrid"
}
```

#### `POST /botgrid/startBot`
เริ่ม WebSocket connection เพื่อรับข้อมูลราคาแบบ Real-time
```json
{
  "message": "WebSocket startBot"
}
```

#### `POST /botgrid/stop`
หยุด WebSocket connection
```json
{
  "message": "WebSocket connection stopped"
}
```

#### `POST /botgrid/test_on_message`
ทดสอบฟังก์ชัน `on_message` ด้วยข้อมูลจำลอง
```json
{
  "e": "trade",
  "E": 1737012330125,
  "s": "XRPUSDT",
  "t": 886915093,
  "p": "3.12020000",
  "q": "2.00000000",
  "T": 1737012330125,
  "m": false,
  "M": true
}
```

#### `POST /botgrid/Backtest`
รัน Backtest ด้วยข้อมูลย้อนหลัง

**Request Body:**
```json
{
  "symbol": "XRPUSDT",
  "tf": "1m",
  "datefrom": "18-12-2024",
  "dateto": "18-12-2025",
  // ... other backtest parameters
}
```

#### `POST /botgrid/data_Backtest`
ดึงข้อมูลผลลัพธ์ Backtest

---

### 3. Configuration Routes (`/ConfigBot/*`)

#### `GET /ConfigBot/run`
ตรวจสอบและสร้าง Tables
```json
{
  "message": "OK RUNNING ConfigBot"
}
```

#### `GET /ConfigBot/CheckConfig`
ตรวจสอบการเชื่อมต่อ MongoDB
```json
{
  "connection_details": {
    "host": "localhost",
    "port": 27017,
    "database_name": "BotGrid2025",
    "status": ""
  }
}
```

#### `POST /ConfigBot/key`
ทดสอบการเชื่อมต่อ Binance API และทำการซื้อขาย (สำหรับทดสอบ)

#### `POST /ConfigBot/getBalance`
ดึงยอดเงินในบัญชี Binance (รูปแบบ Text)

#### `POST /ConfigBot/getBalanceJson`
ดึงยอดเงินในบัญชี Binance (รูปแบบ JSON)
```json
[
  {
    "asset": "USDT",
    "free_balance": 1000.0,
    "value_in_usdt": 1000.0,
    "item_price": 35000.0
  },
  {
    "sum_balance_usdt": 1000.0,
    "sum_balance_thb": 35000.0
  }
]
```

#### `POST /ConfigBot/gethistory`
ดึงประวัติคำสั่งซื้อขาย (รูปแบบ Text)

**Request Body:**
```json
{
  "symbols": ["XRPUSDT", "BNBUSDT"],
  "limit": 10
}
```

#### `POST /ConfigBot/gethistoryJson`
ดึงประวัติคำสั่งซื้อขาย (รูปแบบ JSON)
```json
[
  {
    "symbol": "XRPUSDT",
    "side": "BUY",
    "price": "0.4722",
    "executed_qty": 1273.0,
    "quote_qty": 601.0,
    "time": "2024-12-18 10:30:00"
  }
]
```

#### `POST /ConfigBot/getSumary`
ดึงสรุปบัญชี 30 วันล่าสุด

#### `GET /ConfigBot/getSetting`
ดึงการตั้งค่าปัจจุบันจาก `Setting.js`

#### `POST /ConfigBot/update`
อัปเดตการตั้งค่าใน `Setting.js`

**Request Body:**
```json
{
  "Connetion": {
    "DATA_HOST": "localhost",
    "DATA_PORT": "27017",
    "DATA_NAME": "BotGrid2025",
    "DATA_USER": "",
    "DATA_PASSWORD": ""
  }
}
```

---

### 4. Price Information Routes (`/infoPrice/*`)

#### `GET /infoPrice/run`
ตรวจสอบว่า Price Info module ทำงาน
```json
{
  "message": "OK RUNNING info Price"
}
```

#### `POST /infoPrice/getprice`
ดึงข้อมูลราคา OHLC จาก MongoDB

**Request Body:**
```json
{
  "symbol": "XRPUSDT",
  "tf": "1m",
  "getAll": false,
  "datefrom": "18-12-2024",
  "dateto": "18-12-2025",
  "ohlc": "ohlc"
}
```

#### `POST /infoPrice/getprice_start`
ดึงข้อมูลราคา OHLC จาก MongoDB (เริ่มต้น)

#### `POST /infoPrice/Load_bar_lazy`
โหลดข้อมูลราคาแบบ Lazy Loading

#### `GET /infoPrice/date`
ดึงวันที่ที่มีข้อมูลในฐานข้อมูล

#### `POST /infoPrice/loadPrice`
โหลดข้อมูลราคาจาก Binance API และบันทึกลง MongoDB

**Request Body:**
```json
{
  "symbol": "XRPUSDT",
  "tf": "1m",
  "getAll": false,
  "datefrom": "18-12-2024",
  "dateto": "18-12-2025",
  "ohlc": "ohlc"
}
```

#### `POST /infoPrice/delete`
ลบข้อมูลจาก Collection ที่ระบุ

**Request Body:**
```json
{
  "tableName": "XRPUSDT_1m"
}
```

---

### 5. Price Update Route

#### `POST /update_price/`
อัปเดตราคาและแจ้งเตือน Real-time

**Request Body:**
```json
{
  "price": 0.4722
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Price updated successfully",
  "data": 0.4722
}
```

## 🔧 การใช้งาน

### 1. เริ่มต้นใช้งาน

1. **ตั้งค่า MongoDB** - แก้ไข `Setting.js` ให้ตรงกับการตั้งค่า MongoDB ของคุณ
2. **ตั้งค่า Binance API** - เพิ่ม API Key และ Secret Key ใน `Function/MongoDatabase.py`
3. **รันเซิร์ฟเวอร์** - `python FastAPI_BotGrid2025.py`
4. **ทดสอบ API** - เปิด http://localhost:45441/docs

### 2. เริ่มใช้งาน BotGrid

```bash
# 1. เริ่ม WebSocket เพื่อรับข้อมูลราคา
POST /botgrid/startBot

# 2. Bot จะเริ่มทำงานอัตโนมัติเมื่อได้รับข้อมูลราคาใหม่
# 3. ตรวจสอบสถานะ
GET /botgrid/run
```

### 3. โหลดข้อมูลราคาย้อนหลัง

```bash
# โหลดข้อมูลราคาจาก Binance API
POST /infoPrice/loadPrice
{
  "symbol": "XRPUSDT",
  "tf": "1m",
  "datefrom": "01-01-2024",
  "dateto": "31-12-2024"
}

# ดึงข้อมูลราคาจากฐานข้อมูล
POST /infoPrice/getprice
{
  "symbol": "XRPUSDT",
  "tf": "1m",
  "datefrom": "01-01-2024",
  "dateto": "31-12-2024"
}
```

### 4. รัน Backtest

```bash
POST /botgrid/Backtest
{
  "symbol": "XRPUSDT",
  "tf": "1m",
  "datefrom": "01-01-2024",
  "dateto": "31-12-2024",
  // ... other parameters
}
```

## ⚙️ การตั้งค่า

### MongoDB Configuration

แก้ไขไฟล์ `Setting.js`:

```javascript
var data = {
    "Connetion": {
        "DATA_HOST": "localhost",      // MongoDB Host
        "DATA_PORT": "27017",          // MongoDB Port
        "DATA_NAME": "BotGrid2025",    // Database Name
        "DATA_USER": "",                // Username (ว่างเปล่าถ้าไม่มี)
        "DATA_PASSWORD": ""            // Password (ว่างเปล่าถ้าไม่มี)
    }
}
```

### Binance API Configuration

แก้ไขไฟล์ `Function/MongoDatabase.py`:

```python
ConnetBinace = {
    "API_KEY": "YOUR_API_KEY",
    "API_SECRET": "YOUR_SECRET_KEY",
    "LINE_ADMIN": "YOUR_LINE_TOKEN",      # สำหรับส่งแจ้งเตือน
    "LINE_ADMIN2": "YOUR_LINE_TOKEN_2"
}
```

## 📦 Dependencies หลัก

- **fastapi[all]**: Web Framework
- **uvicorn[standard]**: ASGI Server
- **python-binance**: Binance API Client
- **pymongo**: MongoDB Driver
- **websocket-client**: WebSocket Client
- **websockets**: Async WebSocket Library
- **pydantic**: Data Validation

## 🔒 ความปลอดภัย

⚠️ **คำเตือนสำคัญ:**

1. **อย่าเปิดเผย API Keys** - อย่า Commit API Keys และ Secret Keys ลง Git
2. **ใช้ Environment Variables** - ควรใช้ environment variables สำหรับข้อมูลสำคัญ
3. **ตั้งค่า CORS** - ปรับ CORS settings ให้เหมาะสมกับ production
4. **ตรวจสอบ Permissions** - ตรวจสอบว่า Binance API Key มี permissions ที่เหมาะสม

## 🐛 การแก้ปัญหา

### ปัญหา: ไม่สามารถเชื่อมต่อ MongoDB

**วิธีแก้:**
1. ตรวจสอบว่า MongoDB ทำงานอยู่
2. ตรวจสอบการตั้งค่าใน `Setting.js`
3. ตรวจสอบ Firewall และ Network

### ปัญหา: Binance API Error

**วิธีแก้:**
1. ตรวจสอบ API Key และ Secret Key
2. ตรวจสอบ Network Connection
3. ตรวจสอบ API Permissions

### ปัญหา: WebSocket ไม่ทำงาน

**วิธีแก้:**
1. ตรวจสอบ Internet Connection
2. ตรวจสอบว่า Binance WebSocket URL ถูกต้อง
3. ตรวจสอบ Firewall Settings

## 📝 หมายเหตุ

- โปรเจกต์นี้ใช้สำหรับการซื้อขายจริง - ใช้ด้วยความระมัดระวัง
- ควรทดสอบ Backtest ก่อนใช้งานจริง
- ตรวจสอบ Balance และ Risk Management อย่างสม่ำเสมอ

## 📞 การติดต่อ

สำหรับคำถามหรือปัญหา กรุณาตรวจสอบ:
- API Documentation: http://localhost:45441/docs
- Log Files: ตรวจสอบ Console Output

## 📄 License

โปรเจกต์นี้เป็นโปรเจกต์ส่วนตัว

---

**สร้างโดย:** BotGrid 2025 Team  
**อัปเดตล่าสุด:** 2025

