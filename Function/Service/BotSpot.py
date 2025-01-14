
from logging import exception
import time
import ccxt
import json
from line_notify import LineNotify

from googletrans import Translator
import pprint as pprint

from binance.client import Client
import cryptocode
translator = Translator()

def price_sl(entry, price):
    '''
    $ is point price TP
    % cal from entry to %
    '''
    
    t_sl = float(price.strip('%'))
    if ('$' in price):
        t_sl = t_sl
    elif ('%' in price):
        t_sl = entry - ((entry * t_sl / 100))
    else:
        t_sl = price
    return t_sl
def price_tp(entry, price):
    '''
    $ is point price TP
    % cal from entry to %
    '''
    
    t_sl = float(price.strip('%'))
    if ('$' in price):
        t_sl = t_sl
    elif ('%' in price):
        t_sl = entry + ((entry * t_sl / 100))
    else:
        t_sl = price
    return t_sl
print(price_sl(0.4928,'15%'))

def de_data():
    # เปลี่ยนเป็นคำอะไรก๊ได้ที่ชอบ ให้เหมือนกันทั้ง en_data,de_data
    key = 'T45'
    decrypted = ''
    data = "2U3s1cf/Yf6H+s8Bez+/BMJ5aWFl+z3YwIT6koYbgmePRdTtzJhwAt0Tv7Eaxkwb9kvQ/WzLOwb8cu2sVrRWwQ==*x6yoLP0SX7fSEmZTs8cukA==*z02G9vzN8xkJGGjqqZ/0Jw==*RfvmamCQYGcAv2xPiuiDPA=="

    if data != '':
        decrypted = cryptocode.decrypt(data, key)
    return decrypted
# joint_limit = sell | buy
# joinlimit_tp 


def trad(symbol_in,side_,amount_in,joint_limit,joinlimit_tp,joinlimit_sl):
    ''' 
    amount_in = '@15' is coin '$15' is USD
    joint_limit = sell | buy
    joinlimit_tp = 15% or 15$
    joinlimit_sl = 15% or 15$
    trad( str , [buy,sell] ,flot ,sell | buy, joinlimit_tp,joinlimit_sl)  '''
    text_error = ''
    joinlimit_tp_ = ''
    joinlimit_sl_ = ''
    Type_Order = list(amount_in)[0]
    amount_in = float(amount_in[1:])
    Label_API = "BtoGrid Scaping"
    with open('config.json') as f:
        dataconfig = json.load(f)
    ConnetBinace = dataconfig["ConnetBinace"]
    
    notify = LineNotify(ConnetBinace['LINE_ADMIN'])
    
    API_KEY_C = ConnetBinace['API_KEY']
    API_SECRET = ConnetBinace['API_SECRET']
    
    connect_Binace = ''
    
    try:
        connect_Binace = ccxt.binance({
            'apiKey': API_KEY_C,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'type': 'spot'
        })
        
    except:
        text_error = '! error connect_Binace : "apiKey" '
        notify.send(text_error)
        
    try:
        symbol_ = connect_Binace.fetch_ticker(
            symbol_in)['symbol']  # FTMUSDT FTM/USDT
    except Exception as e:
        text_error = '! error format : "symbol[2]" : ' + \
            symbol_in + '| ' + str(e)
        notify.send(text_error)
        
        print(text_error)
        return text_error
    # symbol FTM/USDT FTM/BNB
    unit = symbol_.split("/")
    
    # ราคาเหรียญล่าสุด
    Coind_last_Price = connect_Binace.fetch_ticker(
        symbol_in)['last']  # ราคาเหรียญล่าสุด
    #Coind_last_Price = 273.2
    
    quantity_coind = 0.0
    
    amount_in = float(amount_in)
    
    coin_main_last = 0.0

    if unit[1] != 'USDT':
        coin_main_last = connect_Binace.fetch_ticker(
            unit[1]+'USDT')['last']
    else:
        pass
    Coind_balance_main = ""
    Coind_balance_Secondary = ""
    try:
        # จำนวน Coind กลัก BTCUSDT =  (USDT)  : FTMBNB = (BNB) ที่ถือ
        Coind_balance_main = connect_Binace.fetch_total_balance()[unit[1]]
    # จำนวน Coind รอง BTCUSDT =  (BTC) : FTMBNB = (FTM)  ที่ถือ
    except exception as e:
        pass
    
    try:
        Coind_balance_Secondary = connect_Binace.fetch_total_balance()[unit[0]]
    #Coind_balance_main = 424.20536
    # ซื้อ n% ของเงินที่มี

    except exception as e:
        pass

    side_ = side_.lower()
    
    #
    #
    # ฟังชั่น connect_Binace.amount_to_precision(symbol_in,999) ช่วยคำนวนปริมาณสั่งซื้อขายให้พอดีกับ จำนวนที่รองรับบนกระดานซื้อขาย
    if Type_Order == '@':  # ซื้อด้วยจำนวนเหรียญ FTM BTC BNB
        # ปริมาณ มูลค่า
        quantity_coind = float(connect_Binace.amount_to_precision(
            symbol_in,  amount_in))  # 15 ,15
        # มูลค่า USDT = จำนวนcoind ที่จะซื้อขาย x ราคาล่าสุด
        # เช็กถ้าไม่ใช่คู่ BTCUSDT ให้คำนวนมูลค่า USDT ใหม่
        main_val = 0.0
        in_USDT = 0.0
        if unit[1] != 'USDT':  # FTMBNB
            main_val = quantity_coind * Coind_last_Price
            in_USDT = coin_main_last * main_val
        else:
            in_USDT = quantity_coind * Coind_last_Price
            main_val = in_USDT
        if side_ == 'buy':
            # มูล่า USDT = จำนวนเหรียญ x ราคาล่าสุด
            # เช็กมูลค่าซื้อขั้นต่ำ พอซื้อขายหรือไม่
            if in_USDT < 10:
                text_error = 'Order value must be a minimum of 10 USDT\nมูลค่าการสั่งซื้อต้องไม่ต่ำกว่า 10 USDT'
                notify.send(text_error)
                # fu_Mysql.GET_Alert_insert(UserID, API_KEY, botAction,  Type_Order + ' '+side_,
                #                           str(Coind_last_Price)+' '+unit[1], str(quantity_coind)+' '+unit[0], str(in_USDT)+' '+unit[1], symbol_in, Pass_in, strategy_, Price_Action, text_error)
                print(text_error)
                return text_error
            # จำนวน Coins หลัก ที่เหลือ <  มูลค่าที่สั่ง
            # เช็กมูลค่า Coindหลัก พอซื้อหรือไม่
            elif Coind_balance_main < main_val:
                text_error = 'not enough quantity balance to buy \nปริมาณคงเหลือไม่เพียงพอที่จะซื้อ'
                notify.send(text_error)
                # fu_Mysql.GET_Alert_insert(UserID, API_KEY, botAction,  Type_Order + ' '+side_,
                #                           str(Coind_last_Price)+' '+unit[1], str(quantity_coind)+' '+unit[0], str(in_USDT)+' '+unit[1], symbol_in, Pass_in, strategy_, Price_Action, text_error)
                print(text_error)
                return text_error
        if side_ == 'sell':
            # มูล่า USDT = จำนวนเหรียญ x ราคาล่าสุด
            # เช็กมูลค่าซื้อขั้นต่ำ พอซื้อขายหรือไม่
            if in_USDT < 10:
                text_error = 'Order value must be a minimum of 10 USDT\nมูลค่าการขายต้องไม่ต่ำกว่า 10 USDT'
                notify.send(text_error)
                # fu_Mysql.GET_Alert_insert(UserID, API_KEY, botAction,  Type_Order + ' '+side_,
                #                           str(Coind_last_Price)+' '+unit[1], str(quantity_coind)+' '+unit[0], str(in_USDT)+' '+unit[1], symbol_in, Pass_in, strategy_, Price_Action, text_error)
                print(text_error)
                return text_error
            # จำนวน Coind ที่เหลือ <  มูล่า Coind ที่สั่งมั้ย
            # เช็กมูลค่า Coind รอง พอขาย หรือไม่
            elif Coind_balance_Secondary < quantity_coind:
                # ปริมาณไม่เพียงพอ
                text_error = 'not enough quantity balance to sell\nปริมาณคงเหลือไม่พอขาย'
                notify.send(text_error)
                # fu_Mysql.GET_Alert_insert(UserID, API_KEY, botAction,  Type_Order + ' '+side_,
                                        #   str(Coind_last_Price)+' '+unit[1], str(quantity_coind)+' '+unit[0], str(in_USDT)+' '+unit[1], symbol_in, Pass_in, strategy_, Price_Action, text_error)
                print(text_error)
                return text_error
    elif Type_Order == '$':
        # แปลงจำนวน USDT เป็น Coind
        quantity_coind = float(connect_Binace.amount_to_precision(
            symbol_in,  float(amount_in) / Coind_last_Price))
        # BNB / ราคาFTMBNB = จำนวน FTM
        #           1 FTM = 0.001936 BNB
        # 20.0 BNB/ 0.001936 BNB  = 10,330.57851239669 FTM
        # 0.0033 BNB / 0.001936 BNB = 1.704545454545455 FTM
        # 0.041 / 0.0019205 = 21.3486071336

        # แปลงจากรูปแบบจำนวนที่ซื้อได้ มาเช็กใหม่
        # มูลค่าที่จะซื้อได้ = ราคาล่าสุด * จำนวน coind
        main_val = Coind_last_Price * quantity_coind
        # 0.0019205 * 21.0 = 0.0403305
        # เช็กถ้าไม่ใช่คู่ BTCUSDT ให้คำนวนมูลค่า USDT ใหม่
        in_USDT = 0.0
        if unit[1] != 'USDT':
            in_USDT = coin_main_last * main_val
            # 386.9 *0.0403305 = 15.6038
        else:
            in_USDT = main_val

        if side_ == 'buy':

            # มูล่า USDT = จำนวนเหรียญ x ราคาล่าสุด
            # เช็กมูลค่าซื้อขั้นต่ำ พอซื้อขายหรือไม่
            if in_USDT < 10:
                text_error = 'Order value must be a minimum of 10 USDT\nมูลค่าการสั่งซื้อต้องไม่ต่ำกว่า 10 USDT'
                notify.send(text_error)
                print(text_error)
                return text_error
            # จำนวน USDT ที่เหลือ <  มูล่า USDTที่สั่ง
            # เช็กมูลค่า USDT ที่มี พอซื้อขายหรือไม่
            elif Coind_balance_main < main_val:
                text_error = 'not enough quantity balance to buy \nปริมาณคงเหลือไม่เพียงพอที่จะซื้อ'
                notify.send(text_error)
                print(text_error)
                return text_error
            print(side_, quantity_coind, in_USDT)

        if side_ == 'sell':

            # มูล่า USDT = จำนวนเหรียญ x ราคาล่าสุด
            # เช็กมูลค่าซื้อขั้นต่ำ พอซื้อขายหรือไม่
            if in_USDT < 10:
                text_error = 'Order value must be a minimum of 10 USDT\nมูลค่าการขายต้องไม่ต่ำกว่า 10 USDT'
                notify.send(text_error)
                print(text_error)
                return text_error
            # จำนวน Coind ที่เหลือ <  มูล่า Coind ที่สั่งมั้ย
            # เทียบกับเหรียญที่ถืออยู่พอขายมั้ย
            elif Coind_balance_Secondary < quantity_coind:
                # ปริมาณไม่เพียงพอ
                text_error = 'not enough quantity balance to sell\nปริมาณคงเหลือไม่พอขาย'
                notify.send(text_error)
                print(text_error)
                return text_error
    # ต้องเป็นจำนวนเหรียญ
    amount = quantity_coind
    price_Action = ''
    as_usdt = ''
    RUNTEST = False
    #    ======= ทำการซื้อ ขาย =======   #
    ###[         Action Real           ]###
    try:

        print(symbol_in, 'market',  side_, amount)
        sss = ''
        sss_limit = ''
        sell_joint = ''
        if RUNTEST:
            quantity = amount  # จำนวนเหรียญ
            price_Action = Coind_last_Price  # ราคาเหรียญ
        else:
            quantity = 0
            try:
                if side_ == 'sell':
                    if joint_limit == 'sell':
                        sell_joint = 'on'
                        quantity = amount  # จำนวนเหรียญ
                        price_Action = Coind_last_Price  # ราคาเหรียญ
                    else:
                        sss = connect_Binace.create_order(
                            symbol_in, 'market',  side_, amount)  # , order_price
                        quantity = float(sss['amount'])  # จำนวนเหรียญ
                        price_Action = float(sss['average'])  # ราคาเหรียญ
                    # กรณีเล่นแบบ SHORT ให้ตั้งขาย กำหนด joint_limit = buy ตอนขาย จะเก็บค่าใว้เช็กให้ซื้อ
                        if joint_limit == 'buy':
                            # ตั้ง รอซื้อ เล่นแบบ SHORT
                            side_will = 'buy'
                            side_ = 'buy'
                            joint_limit = '-'
                            # fu_Mysql.insert_order(strategy_,  datetime.now().strftime("%Y-%m-%d %H:%M:%S"), side_will,  symbol_in,  str(price_limit), str(quantity),
                            #                       str(amount), status, Pass_in, json.dumps(data))

                elif side_ == 'buy':

                    pass
                    sss = connect_Binace.create_order(
                        symbol_in, 'market',  side_, amount)  # , order_price
                    quantity = float(sss['amount'])  # จำนวนเหรียญ
                    price_Action = float(sss['average'])  # ราคาเหรียญ

                # joint_limit สำหรับบอท Grit
                if joint_limit == 'sell' and side_ == 'buy':
                    time.sleep(1)
                    # sss_limit = connect_Binace.create_order(
                    #    symbol_in, 'limit',  'sell', amount, price_limit)
                    # ตั้งขาย
                    side_will = 'sell'
                    side_ = 'sell'
                    joint_limit = '-'
                    # fu_Mysql.insert_order(strategy_,  datetime.now().strftime("%Y-%m-%d %H:%M:%S"), side_will,  symbol_in, str(price_limit), str(quantity),
                    #                       str(amount), status, Pass_in, json.dumps(data))
                if joinlimit_tp != None and joinlimit_tp != '' and joinlimit_tp != '-':
                    Limitp = price_tp(price_Action, str(joinlimit_tp))
                    
                    sss_limit = connect_Binace.create_order(
                        symbol_in, 'limit',  'sell', amount, Limitp)
                    joinlimit_tp_ = True
                    print(sss_limit)

                if joinlimit_sl != None and joinlimit_sl != '' and joinlimit_sl != '-':
                    stopLimisl = price_sl(price_Action, (joinlimit_sl))
                    params = {
                        'stopPrice': stopLimisl
                    }
                    sss_limit_SL = connect_Binace.create_order(
                        symbol_in, 'STOP_LOSS_LIMIT',  'sell', amount, stopLimisl,  params)
                    joinlimit_sl_ = True
                    print(sss_limit_SL)
                    
                    
            except Exception as e:

                text_error = 'API Binace Error : '+str(e)
                notify.send(text_error)
                # fu_Mysql.GET_Alert_insert(UserID, API_KEY, botAction, Type_Order + ' '+side_,
                #                           str(Coind_last_Price)+' '+unit[1], str(quantity_coind)+' '+unit[0], str(in_USDT)+' '+unit[1], symbol_in, Pass_in, strategy_, Price_Action, text_error)
                print(text_error)
                return text_error

        # # จำนวน USDT ที่เหลือ
        balance_Port = connect_Binace.fetch_balance()['USDT']['free']
        print("<<<<<<<<<<<<<<<[ DATA ACTION ]>>>>>>>>>>>>>>>")

        as_usdt = float(("{0:,.2f}").format(quantity * price_Action))
        time.sleep(1)
        # fu_Mysql.GET_Alert_insert(UserID, API_KEY, botAction, Type_Order + ' '+side_, str(price_Action)+' '+unit[1], str(quantity)+' '+unit[0],
        #                           str(as_usdt)+' '+unit[1], symbol_in, Pass_in, strategy_, Price_Action, text_error)

        try:
            # เรียกดูเงินที่ใช้ได้

            stiker_line = ''
            if side_ == 'buy':
                stiker_line = '🟢'
            elif side_ == 'sell':
                stiker_line = '🔴'
            price_in = ''
            # if price_ != '':
            #     price_in = ('\nPrice: {0:,} ').format(
            #         float(price_)) + unit[1]
            if unit[1] == 'USDT':
                # print('Strategy Line: '+ strategy_ )
                messend = ' '+stiker_line+' [ '+side_ + ' ' + unit[0] + ' ]' + price_in + \
                    ('\nPrice : 🛒  {0:,} ' + unit[1] + '\nqty coins : ⚙️ {1:,} ' + unit[0] +
                     '\nMoney : 💵 {2:,.2f} '+unit[1]+'\nUSDT free = {3:,.2f}').format(price_Action, quantity, as_usdt, balance_Port)
            else:  # .format(float(price_Action), float(amount_Action), float(as_usdt), float(Coind_balance_main)))
                messend = ' '+stiker_line+' [ '+side_ + ' ' + unit[0] + ' ] ' + price_in + (
                    '\nPrice : 🛒  {0:,} ' + unit[1] + '\nqty coins : ⚙️ {1:,} ' + unit[0] + '\nMoney : 💵 {2:,} '+unit[1] + '\nUSDT free = {3:,.2f}').format(price_Action, quantity, as_usdt, balance_Port)
                # .format(price_Action, amount_Action, float(as_usdt), float(Coind_balance_main))
            if sell_joint == 'on':
                messend = messend+'\n(Sell on Binace)'
            if joinlimit_tp_ and joinlimit_tp_ != '':
                messend = messend+'\nSet TP :' + joinlimit_tp
            if joinlimit_sl_  and joinlimit_sl_ != '':
                messend = messend+'\nSet SL :' + joinlimit_sl
            print(messend)
            notify.send('💎'+messend)

            return price_Action

        except Exception as e :
            txt_erroe = 'action succeed ! \n🛠  but messend line notify error Failed'

            # fu_Mysql.GET_Alert_insert(UserID, API_KEY, botAction, Type_Order + ' '+side_, str(price_Action)+' '+unit[1], str(quantity)+' '+unit[0],
            #                           str(as_usdt)+' '+unit[1], symbol_in, Pass_in, strategy_, Price_Action, text_error)
            notify.send(txt_erroe)
            print(txt_erroe)
            print(e)
            return txt_erroe
    except Exception as e:

        text_error = '\n🛠 '+Label_API + \
            ' Check API : Enable Spot & Margin Trading 🛠' + str(e)
        notify.send(text_error)
        print(text_error)
        return text_error

symbol_in = 'XRPUSDT'
#  buy  sell
side_ = 'buy'     ; amount_in = '23'      ; joint_limit = 'sell'   ;joinlimit_tp = '5%'; joinlimit_sl = ''
# trad(symbol_in,side_,amount_in,joint_limit,joinlimit_tp,joinlimit_sl)

# print(de_data())

def cancelOrder(orderId,symbol,all):
    
    with open('config.json') as f:
        dataconfig = json.load(f)
    ConnetBinace = dataconfig["ConnetBinace"]
    
    notify = LineNotify(ConnetBinace['LINE_ADMIN'])
    
    API_KEY_C = ConnetBinace['API_KEY']
    API_SECRET = ConnetBinace['API_SECRET']
    
    connect_Binace = ''
    
    try:
        connect_Binace = ccxt.binance({
            'apiKey': API_KEY_C,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'type': 'spot'
        })
        
    except:
        text_error = '! error connect_Binace : "apiKey" '
        notify.send(text_error)
        
    if all:
        cancel_result = connect_Binace.cancel_all_orders(symbol=symbol_in)
    else :
        cancel_result = connect_Binace.cancel_order(id=orderId,symbol=symbol )
    
    translated_text = translator.translate(str(cancel_result), dest='th')
    notify.send(translated_text)

def Create_LimitOrder(amount,Limitp):
    with open('config.json') as f:
        dataconfig = json.load(f)
    ConnetBinace = dataconfig["ConnetBinace"]
    
    notify = LineNotify(ConnetBinace['LINE_ADMIN'])
    
    API_KEY_C = ConnetBinace['API_KEY']
    API_SECRET = ConnetBinace['API_SECRET']
    
    connect_Binace = ''
    
    try:
        connect_Binace = ccxt.binance({
            'apiKey': API_KEY_C,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'type': 'spot'
        })
        
    
        
        sss_limit = connect_Binace.create_order(
                            symbol_in, 'limit',  'sell', amount, Limitp)
        
        notify.send(str(sss_limit))   
        pprint.pprint(sss_limit)      
    except Exception as e:
        text_error = '🛠! error connect_Binace : {0}'.format(e)
        translated_text = text_error+'\n'+translator.translate(str(text_error), dest='th')
        notify.send(translated_text.text)    
# cancelOrder('6105862418','XRPUSDT',False)

# Create_LimitOrder(23,0.5113)

def get_open_limit_sell_orders(symbol):
    with open('config.json') as f:
        dataconfig = json.load(f)
    ConnetBinace = dataconfig["ConnetBinace"]
    
    notify = LineNotify(ConnetBinace['LINE_ADMIN'])
    
    API_KEY_C = ConnetBinace['API_KEY']
    API_SECRET = ConnetBinace['API_SECRET']
    
    
    client = Client(API_KEY_C, API_SECRET)
    # Retrieve all open orders for the specified symbol
    open_orders = client.get_open_orders(symbol=symbol)
    
    # Filter out the limit sell orders
    limit_sell_orders = [order for order in open_orders if order['side'] == 'SELL' and order['type'] == 'LIMIT']
    
    return limit_sell_orders



def get_Id_LimitOrder(symbol):
    # Get all open limit sell orders for the specified symbol
    open_limit_sell_orders = get_open_limit_sell_orders(symbol)
    # Print the open limit sell orders
    for order in open_limit_sell_orders:
        orderId = order['orderId']
        side =  order['side']
        origQty =  order['origQty']
        print(orderId,side,origQty)
        
# get_Id_LimitOrder('XRPUSDT')