'''
期货交易机器人(暂时只支持做多), 并自动推送消息至企业微信
本机器人使用supertrend策略, 可以根据自己的情况修改
交易所的api可以根据自己的情况做修改
'''

import ccxt
import pandas as pd
import warnings
import numpy as np
import pandas_ta as ta
from datetime import datetime
import time
import schedule
from rich.console import Console
import send_msg

__author__ = 'K0uSA0f'

console = Console()

warnings.filterwarnings('ignore')
pd.set_option('display.max_rows',None) # 显示数据的所有行

exchange = ccxt.okx(
        {
            # 填入交易所api的相关信息
            'apiKey': '',
            'secret': '',
            'password': '',
            'timeout': 3000,
        }
    )

atr_length = 10
atr_multiplier = 3.0

symbol = 'ETH-USDT-SWAP'
timeframe = '30m'

def indicators(data):
    df = data.ta.supertrend(high=data['high'],low=data['low'],close=data['close'],length=atr_length,multiplier=atr_multiplier)
    df['high'] = data['high']
    df['low'] = data['low']
    df['close'] = data['close']
    df['dt'] = data['dt']
    return df

def get_account_value():
    balance = exchange.fetch_balance()
    return balance['free']['USDT']

def check_buy_sell_signals(df):
    last_row_index = len(df.index) - 1
    latest_price = round(df['close'].iloc[-1], 2)
    
    # 返回1对应上升趋势 返回-1对应下降趋势
    latest_direction = df[f'SUPERTd_{atr_length}_{atr_multiplier}'].iloc[-1]
    
    # 上升趋势的下轨的值
    latest_long_value = round(df[f'SUPERTl_{atr_length}_{atr_multiplier}'].iloc[-1],2)
    
    # 下降趋势的上轨的值
    latest_short_value = round(df[f'SUPERTs_{atr_length}_{atr_multiplier}'].iloc[-1],2)
    
    signal_value = latest_long_value if latest_direction else latest_short_value    
    console.log(f"[green][+] Price: {latest_price}; Direction: {latest_direction}; Signal value: {signal_value}")

    # 在下降趋势中收盘价格突破上轨做多
    long_condition = latest_direction < 0 and latest_price > latest_short_value
    if long_condition:
        # 开多
        # order_open_long = exchange.create_order(symbol,type='market', side='buy',amount=1,params={"tdMode":'cross',"posSide":"long"})
        console.log(f'[green][+] {symbol}开多:{latest_price}')
        send_msg.sendMsg(f'{symbol}触发买入信号, 开多:{latest_price}', '@all')
    
    # 在上升趋势中收盘价格跌破下轨平多
    short_condition = latest_direction > 0 and latest_price < latest_long_value
    if short_condition:
        # 平多
        try:
            order_close_long = exchange.create_order(symbol,type='market', side='sell',amount=1,params={"tdMode":'cross',"posSide":"long",})
            console.log(f'[green][+] {symbol}触发卖出信号, 平多:{latest_price}')
            send_msg.sendMsg(f'{symbol}触发卖出信号, 平多:{latest_price}', '@all')
        except Exception as e:
            console.log("[yellow][!] 不存在多单平仓失败! Error: ",e)
            send_msg.sendMsg('不存在多单平仓失败!', '@all')

def run_bot():
    console.log(f"[green][+] Fetching n3w bars for {datetime.now().isoformat()}")
    bars = exchange.fetch_ohlcv(symbol,timeframe,limit=200) # 最新的200条数据
    df = pd.DataFrame(bars[:],columns=['timestamp','open','high','low','close','volume'])
    df['dt'] = pd.to_datetime(df['timestamp'],unit='ms')
    df = indicators(df)
    # print(df)

    check_buy_sell_signals(df)

def main():
    # 每10秒执行一次
    schedule.every(10).seconds.do(run_bot)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            console.log("[yellow][!] Bye!")
            exit()



