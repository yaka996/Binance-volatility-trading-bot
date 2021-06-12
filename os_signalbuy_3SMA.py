from tradingview_ta import TA_Handler, Interval, Exchange

# used for dates
from datetime import date, datetime, timedelta
import time

# use for environment variables
import os
# use if needed to pass args to external modules
import sys
# used for directory handling
import glob
import time
import threading

# for colourful logging to the console
class txcolors:
    BUY = '\033[92m'
    WARNING = '\033[93m'
    SELL_LOSS = '\033[91m'
    SELL_PROFIT = '\033[32m'
    DIM = '\033[2m\033[35m'
    DEFAULT = '\033[39m'

INTERVAL1MIN = Interval.INTERVAL_1_MINUTE # Main Timeframe for analysis on Oscillators and Moving Averages (15 mins)
INTERVAL5MIN = Interval.INTERVAL_5_MINUTES # Main Timeframe for analysis on Oscillators and Moving Averages (15 mins)

EXCHANGE = 'BINANCE'
SCREENER = 'CRYPTO'
PAIR_WITH = 'USDT'
TICKERS = 'tickers.txt' #'signalsample.txt'

TIME_TO_WAIT = 1 # Minutes to wait between analysis
DEBUG = False # List analysis result to console

SIGNAL_NAME = 'os_signalbuys_3SMA'
SIGNAL_FILE_BUY = 'signals/' + SIGNAL_NAME + '.buy'

TRADINGVIEW_EX_FILE = 'tradingview_ta_unknown'

def analyze(pairs):

    signal_coins = {}

    analysis1MIN = {}
    handler1MIN = {}

    analysis5MIN = {}
    handler5MIN = {}
    
    if os.path.exists(SIGNAL_FILE_BUY):
        os.remove(SIGNAL_FILE_BUY)
        
    if os.path.exists(TRADINGVIEW_EX_FILE):
        os.remove(TRADINGVIEW_EX_FILE)

    for pair in pairs:
        handler1MIN[pair] = TA_Handler(
            symbol=pair,
            exchange=EXCHANGE,
            screener=SCREENER,
            interval=INTERVAL1MIN,
            timeout= 10)
        handler5MIN[pair] = TA_Handler(
            symbol=pair,
            exchange=EXCHANGE,
            screener=SCREENER,
            interval=INTERVAL5MIN,
            timeout= 10)
                        
    for pair in pairs:
        try:
            analysis1MIN = handler1MIN[pair].get_analysis()
            analysis5MIN = handler5MIN[pair].get_analysis()
        except Exception as e:
            print(f'{SIGNAL_NAME}Exception:')
            print(e)
            print (f'Coin: {pair}')
            print (f'handler: {handler1MIN[pair]}')
            print (f'handler2: {handler5MIN[pair]}')
            with open(TRADINGVIEW_EX_FILE,'a+') as f:
                    f.write(pair.removesuffix(PAIR_WITH) + '\n')
            continue
        
        SMA5_1MIN = round(analysis1MIN.indicators['SMA5'],2)
        SMA10_1MIN = round(analysis1MIN.indicators['SMA10'],2)
        SMA20_1MIN = round(analysis1MIN.indicators['SMA20'],2)

        SMA5_5MIN = round(analysis5MIN.indicators['SMA5'],2)
        SMA10_5MIN = round(analysis5MIN.indicators['SMA10'],2)
        SMA20_5MIN = round(analysis5MIN.indicators['SMA20'],2)
        
        ACTION = 'NOTHING'
        
        # Buy condition on the 1 minute indicator
        if (SMA20_1MIN < SMA10_1MIN) and (SMA10_1MIN < SMA5_1MIN):
            # Sell condition on the 5 minute indicator
            if (SMA20_5MIN > SMA10_5MIN) and (SMA10_5MIN > SMA5_5MIN):
                # i.e. 5 minutes ago it was a sell, but now it's a buy
                ACTION = 'BUY'

        # if DEBUG:
        print(f'{SIGNAL_NAME} Signals {pair} {ACTION} - SMA20_1MIN: {SMA20_1MIN} SMA10_1MIN: {SMA10_1MIN} SMA5_1MIN: {SMA5_1MIN}')
        print(f'{SIGNAL_NAME} Signals {pair} {ACTION} - SMA20_5MIN: {SMA20_5MIN} SMA10_5MIN: {SMA10_5MIN} SMA5_5MIN: {SMA5_5MIN}')

        if ACTION == 'BUY':
            signal_coins[pair] = pair
            if DEBUG:
                print(f'{txcolors.BUY}{SIGNAL_NAME}: {pair} - Buy Signal Detected{txcolors.DEFAULT}')
            with open(SIGNAL_FILE_BUY,'a+') as f:
                f.write(pair + '\n')
            
            timestamp = datetime.now().strftime("%d/%m %H:%M:%S")
            with open(SIGNAL_NAME + '.log','a+') as f:
                f.write(timestamp + ' ' + pair + '\n')
                f.write(f'    Signals: {ACTION} - SMA20_1MIN: {SMA20_1MIN} SMA10_1MIN: {SMA10_1MIN} SMA5_1MIN: {SMA5_1MIN}')
                f.write(f'    Signals: {ACTION} - SMA20_5MIN: {SMA20_5MIN} SMA10_5MIN: {SMA10_5MIN} SMA5_5MIN: {SMA5_5MIN}')
                
        if ACTION == 'NOTHING':
            if DEBUG:
                print(f'{SIGNAL_NAME}: {pair} - not enough signal to buy')
            
    return signal_coins

def do_work():
    try:
        while True:
            if not os.path.exists(TICKERS):
                time.sleep((TIME_TO_WAIT*60))
                continue

            signal_coins = {}
            pairs = {}

            pairs=[line.strip() for line in open(TICKERS)]
            for line in open(TICKERS):
                pairs=[line.strip() + PAIR_WITH for line in open(TICKERS)] 
            
            if not threading.main_thread().is_alive(): exit()
            print(f'{SIGNAL_NAME}: Analyzing {len(pairs)} coins')
            signal_coins = analyze(pairs)
            #if len(signal_coins) == 0:
            #    print(f'{SIGNAL_NAME}: No coins above sell threshold on three timeframes. Waiting {TIME_TO_WAIT} minutes for next analysis')
            #else:
            #    print(f'{SIGNAL_NAME}: {len(signal_coins)} coins with Buy signals. Waiting {TIME_TO_WAIT} minutes for next analysis')
            print(f'{SIGNAL_NAME}: {len(signal_coins)} coins with Buy Signals. Waiting {TIME_TO_WAIT} minutes for next analysis.')

            time.sleep((TIME_TO_WAIT*60))
    except Exception as e:
            print(f'{SIGNAL_NAME}: Exception: {e}')