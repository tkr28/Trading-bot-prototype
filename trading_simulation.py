
import websocket, json, pandas
import winsound
import ta
import ccxt
import pandas as pd
from ta.trend import EMAIndicator

    
duration = 1000
freq = 450
long_in_position = False
symbol =input("write a symbol = ").lower()
wma_value = int(input("write a number for wma value = "))
ema_value = int(input("write a number for ema value = "))
"""EVERY VARIABLE WHICH YOU CHOOSE COULD BE WRITTEN IN INPUT FORMAT"""
position_result = 0
position_type = ''
entry_position_type = 'LONG'
entry_time = 0
profit = 0
loss = 0
interval = "1 minute"
target_profit = 0
budget = 10
leverage = 20
entry_price = 0
tp = 0.005
sl = 0.005
take_profit_price = 0        
stop_loss_price = 0
commission = 0.04 
coin_amount = 0
win = 0
lose = 0
operation_number = 0
winRate = 0

SOCKET = f"wss://fstream.binance.com/ws/{symbol}usdt@kline_1m"

ex = ccxt.binance()
ohlcv = ex.fetch_ohlcv(f'{symbol.upper()}/USDT:USDT', '1m', limit=100)
af = pd.DataFrame(ohlcv, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
af['date'] = pd.to_datetime(af['date'], unit='ms')
af.set_index('date', inplace=True)
af = af.sort_index(ascending=True)

#Dropping is essential because last row data is not closed
af.drop(af.index[-1], inplace=True)


zf = pd.DataFrame()

df = pandas.DataFrame()

 
sql_storage = pd.DataFrame()


def on_open(ws):
    
    print("opened connection")

def on_close(ws):

    print("closed connection")
    
def on_message(ws, message):
    global df, budget, leverage, commission, win, lose, operation_number, winRate, interval
    global long_in_position,coin_amount, loss, entry_position_type
    global take_profit_price,entry_price, stop_loss_price, target_profit, tp, sl, af, profit 
    global entry_time, wma_value, ema_value, position_result, position_type , zf, sql_storage
    # print("received message: ")
    json_message = json.loads(message)
    #print(json_message)
    #pprint.pprint(json_message
    candle = json_message['k']

    close = candle['c']
    
    is_candle_closed = candle['x']

     # TP SL FOR LONG
    if float(close) >= take_profit_price and long_in_position:
        
        budget = budget +  ((float(close) - entry_price) * coin_amount)
        budget = budget - ((budget/100) * commission * leverage)
        profit =  ((take_profit_price - entry_price) * coin_amount)
        
        operation_number += 1 
        win += 1
        winRate = (win / operation_number) * 100
        print("Take profit!!!")
        print("BUDGET =", budget)
        print("Win = ", win, "Lose = ", lose, "Win rate = ", winRate)
     
        long_in_position = False
        
        position_type = 'TAKE PROFIT'
        position_result = profit
        
        cf = pandas.DataFrame({'ENTRY_POSITION_TYPE': entry_position_type ,'BUDGET': (budget - profit),'LEVERAGE': leverage,'SYMBOL':symbol,'INTERVAL': interval, 'TP':tp,'SL':sl,'ENTRY DATE':entry_time,'END DATE':[pandas.to_datetime(json_message['E'], unit = 'ms')],'EMA_VALUE':int(ema_value),'WMA_VALUE':int(wma_value), 'POSITION_TYPE':position_type, 'POSITION_RESULT':float(position_result)})     
        
        sql_storage = pandas.concat([sql_storage,cf], axis = 0)  
        
        #DO NOT FORGET ADD YOUR FILE PATH
        file_path = r'BLABLABLA.xlsx'
        df.to_excel(file_path, index=False)
        sql_storage.to_excel(file_path, index=False)
        
        
        winsound.Beep(freq, duration)
        
   
    elif float(close) <=  stop_loss_price and long_in_position:
        budget= budget - ((entry_price - float(close)) * coin_amount)
        budget= budget - ((budget/100) * commission * leverage)
        loss = (( stop_loss_price - entry_price ) * coin_amount)
        operation_number += 1 
        lose += 1
        winRate = (win / operation_number) * 100
        print("Stop loss...")
        print("BUDGET =", budget)
        print("Win = ", win, "Lose = ", lose, "Win rate = ", winRate)       
        long_in_position = False 
        position_result = loss
        position_type = 'STOP LOSS'
        
        cf = pandas.DataFrame({'ENTRY_POSITION_TYPE': entry_position_type ,'BUDGET': (budget - loss),'LEVERAGE': leverage,'SYMBOL':symbol,'INTERVAL': interval,'TP':tp,'SL':sl,'ENTRY DATE':entry_time,'END DATE':[pandas.to_datetime(json_message['E'], unit = 'ms')],'EMA_VALUE':int(ema_value),'WMA_VALUE':int(wma_value), 'POSITION_TYPE':position_type, 'POSITION_RESULT':float(position_result)})     
        
        sql_storage = pandas.concat([sql_storage,cf], axis = 0)  
        
        
        #DO NOT FORGET ADD YOUR FILE PATH
        file_path = r'BLABLABLA.xlsx'
        df.to_excel(file_path, index=False)
        sql_storage.to_excel(file_path, index=False)
        
        winsound.Beep(freq, duration)
        
    else:
        pass
    
    
    if is_candle_closed:
        print("candle closed at:" ,close)
        
   
        #COMBINING OHLCV'S AND WEBSOCKET'S CLOSE DATA
        new_value = float(close)
        af = pd.concat([af['close'], pd.Series([new_value])], ignore_index=True, axis=0)
        
        # Rename the column if needed
        af = pd.DataFrame({'close': af})

        # print(af)
       
        #LOAD EMA
        closingEma = EMAIndicator(af["close"], ema_value)
        af["ClosingEMA"] = closingEma.ema_indicator()
        
        #LOAD WMA
        af['ClosingWMA'] = ta.trend.WMAIndicator(close=af['close'], window = wma_value).wma()
        
        
        # BUY SIGNAL
        if len(af) >= 2 and (af["ClosingEMA"].iloc[-2] > af["ClosingWMA"].iloc[-2] and af["ClosingEMA"].iloc[-1] <= af["ClosingWMA"].iloc[-1]) and long_in_position == False:
                
          
            entry_price = af.tail(1).close.values[0] 
            coin_amount = ((budget) * float(leverage)) / float(entry_price)
            budget = budget - ((budget/100) * commission * leverage)
            print("LONG SIGNAL... Entry price =", entry_price)
            print("BUDGET =", budget)
            print("Coin amount is",coin_amount)
            take_profit_price = entry_price * (1 + tp)
            stop_loss_price = entry_price * (1 - sl)
            target_profit = (take_profit_price - entry_price) * coin_amount
            entry_time = [pandas.to_datetime(json_message['E'], unit = 'ms')]
            print("Target profit: $",target_profit)
            print("Target tp price: ",take_profit_price )
            print("Stop loss price: ", stop_loss_price)
            
            
            winsound.Beep(freq, duration)
            long_in_position = True
            
            
        
                
        else: 
                
            pass
            
   

        
    else:
        pass

            
ws = websocket.WebSocketApp(SOCKET, on_open = on_open, on_close = on_close, on_message= on_message)
ws.run_forever()
