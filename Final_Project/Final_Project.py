#PART ONE: connecting to Alpaca (this was horrible)

import alpaca_trade_api as tradeapi
import time
import datetime
from datetime import timedelta
from pytz import timezone
tz = timezone('US/Eastern')

import os
import numpy as np
import pandas as pd

api = tradeapi.REST('PKBHP25E3NCTGKBSGMEC',
                    'x9SkktU9osLK0udkIMjLNJOrXF9PVKMpqUH9bx3H',
                    'https://paper-api.alpaca.markets')

#response = requests.get(url, headers=headers)
#print(response.text)

import logging
logging.basicConfig(filename='./apca_algo.log', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('{} logging started'.format(datetime.datetime.now().strftime("%x %X")))




def get_data_bars(symbols, timeframe, slow, fast):
    bar_data = api.get_bars(symbols, timeframe, limit=500).df
    result = {}

    for symbol in symbols:
        df = bar_data[bar_data['symbol'] == symbol].copy()
        if df.empty:
            print(f"No data for {symbol}")
            continue
        print(f"Columns for {symbol}:", df.columns)
        df['fast_ema'] = df['close'].rolling(window=fast).mean()
        df['slow_ema'] = df['close'].rolling(window=slow).mean()
        result[symbol] = df

    return result



def get_signal_bars(symbol_list, rate, ema_slow, ema_fast):
    data = get_data_bars(symbol_list, rate, ema_slow, ema_fast)
    signals = {}

    for symbol in symbol_list:
        df = data[symbol]
        if df['fast_ema'].iloc[-1] > df['slow_ema'].iloc[-1]:
            signals[symbol] = 1
        else:
            signals[symbol] = 0

    return signals


def time_to_open(current_time):
    if current_time.weekday() <= 4:
        d = (current_time + timedelta(days=1)).date()
    else:
        days_to_mon = 0 - current_time.weekday() + 7
        d = (current_time + timedelta(days=days_to_mon)).date()
    next_day = datetime.datetime.combine(d, datetime.time(9, 30, tzinfo=tz))
    seconds = (next_day - current_time).total_seconds()
    return seconds

def run_checker(stocklist):
    print('run_checker started')
    while True:
        # Check if Monday-Friday
        if datetime.datetime.now(tz).weekday() >= 0 and datetime.datetime.now(tz).weekday() <= 4:
            # Checks market is open
            print('Trading day')
            if datetime.datetime.now(tz).time() > datetime.time(9, 30) and datetime.datetime.now(tz).time() <= datetime.time(15, 30):
                signals = get_signal_bars(stocklist, '5Min', 20, 5)
                for signal in signals:
                    if signals[signal] == 1:
                        if signal not in [x.symbol for x in api.list_positions()]:
                            logging.warning('{} {} - {}'.format(datetime.datetime.now(tz).strftime("%x %X"), signal, signals[signal]))
                            api.submit_order(signal, 1, 'buy', 'market', 'day')
                            # print(datetime.datetime.now(tz).strftime("%x %X"), 'buying', signals[signal], signal)
                    else:
                        try:
                            api.submit_order(signal, 1, 'sell', 'market', 'day')
                            logging.warning('{} {} - {}'.format(datetime.datetime.now(tz).strftime("%x %X"), signal, signals[signal]))
                        except Exception as e:
                            # print('No sell', signal, e)
                            pass

                time.sleep(60)
            else:
                # Get time amount until open, sleep that amount
                print('Market closed ({})'.format(datetime.datetime.now(tz)))
                print('Sleeping', round(time_to_open(datetime.datetime.now(tz))/60/60, 2), 'hours')
                time.sleep(time_to_open(datetime.datetime.now(tz)))
        else:
            # If not trading day, find out how much until open, sleep that amount
            print('Market closed ({})'.format(datetime.datetime.now(tz)))
            print('Sleeping', round(time_to_open(datetime.datetime.now(tz))/60/60, 2), 'hours')
            time.sleep(time_to_open(datetime.datetime.now(tz)))

stocks = ['AA','AAL','AAPL','AIG','AMAT','AMC','AMD',
          'AMGN','AMZN','APA','BA','BABA','BAC','BBY',
          'BIDU','BP','C','CAT','CMG','COP','COST',
          'CSCO','CVX','DAL','DIA','DIS','EBAY',]


# STEP 2: Strategies!

def sma_crossover_strategy(symbol, df):
    signals = []
    for i in range(1, len(df)):
        prev_fast = df['fast_ema'].iloc[i-1]
        prev_slow = df['slow_ema'].iloc[i-1]
        curr_fast = df['fast_ema'].iloc[i]
        curr_slow = df['slow_ema'].iloc[i]

        if np.isnan([prev_fast, prev_slow, curr_fast, curr_slow]).any():
            signals.append("hold")
            continue

        if prev_fast < prev_slow and curr_fast > curr_slow:
            signals.append("buy")
        elif prev_fast > prev_slow and curr_fast < curr_slow:
            signals.append("sell")
        else:
            signals.append("hold")

    df['signal'] = ["hold"] + signals
    return df

def mean_reversion_strategy(symbol, df, window=20, threshold=1.5):
    df = df.copy()
    df['mean'] = df['close'].rolling(window=window).mean()
    df['std'] = df['close'].rolling(window=window).std()
    df['upper'] = df['mean'] + threshold * df['std']
    df['lower'] = df['mean'] - threshold * df['std']
    
    signals = []
    for i in range(len(df)):
        if np.isnan(df['mean'].iloc[i]) or np.isnan(df['std'].iloc[i]):
            signals.append('hold')
        elif df['close'].iloc[i] < df['lower'].iloc[i]:
            signals.append('buy')
        elif df['close'].iloc[i] > df['upper'].iloc[i]:
            signals.append('sell')
        else:
            signals.append('hold')
    
    df['signal'] = signals
    return df

def bollinger_band_strategy(symbol, df, window=20):
    df = df.copy()
    df['mean'] = df['close'].rolling(window).mean()
    df['std'] = df['close'].rolling(window).std()
    df['upper'] = df['mean'] + 2 * df['std']
    df['lower'] = df['mean'] - 2 * df['std']
    
    signals = []
    for i in range(len(df)):
        price = df['close'].iloc[i]
        if np.isnan(df['upper'].iloc[i]) or np.isnan(df['lower'].iloc[i]):
            signals.append('hold')
        elif price < df['lower'].iloc[i]:
            signals.append('buy')
        elif price > df['upper'].iloc[i]:
            signals.append('sell')
        else:
            signals.append('hold')

    df['signal'] = signals
    return df


print('test:')
# test Crossover
test_data = get_data_bars(['AAPL'], '5Min', 20, 5)['AAPL']
result = sma_crossover_strategy('AAPL', test_data)

print(result[['close', 'fast_ema', 'slow_ema', 'signal']].tail())

# Test Mean Reversion
mean_rev = mean_reversion_strategy('AAPL', test_data)
print(mean_rev[['close', 'mean', 'upper', 'lower', 'signal']].tail())

# Test Bollinger
boll = bollinger_band_strategy('AAPL', test_data)
print(boll[['close', 'mean', 'upper', 'lower', 'signal']].tail())


#run_checker(stocks)

#STEP 3 Short selling (Track and simulate)

def simulate_trades(symbol, df):
    position = None
    buy_price = 0
    sell_price = 0
    profit = 0

    for i in range(len(df)):
        signal = df['signal'].iloc[i]
        price = df['close'].iloc[i]

        if signal == "buy":
            if position == "short":
                profit += sell_price - price  # Cover short
                position = None
            elif position is None:
                buy_price = price
                position = "long"

        elif signal == "sell":
            if position == "long":
                profit += price - buy_price  # Exit long
                position = None
            elif position is None:
                sell_price = price
                position = "short"

    return round(profit, 2)


#(Actually Trade)
import json

def execute_trade(symbol, df, strategy_name, executed_trades):
    signal = df['signal'].iloc[-1]
    price = df['close'].iloc[-1]
    positions = {pos.symbol: float(pos.qty) for pos in api.list_positions()}

    # Strategy-specific quantity logic
    def get_strategy_qty():
        if strategy_name == "bollinger_bands" and 'lower' in df.columns and 'std' in df.columns:
            deviation = (df['mean'].iloc[-1] - price) / df['std'].iloc[-1]
            if deviation > 1.5:
                return 3
            elif deviation > 1.0:
                return 2
        elif strategy_name == "mean_reversion" and 'lower' in df.columns and 'std' in df.columns:
            deviation = (df['mean'].iloc[-1] - price) / df['std'].iloc[-1]
            if deviation > 1.5:
                return 2
        elif strategy_name == "sma_crossover":
            gap = df['fast_ema'].iloc[-1] - df['slow_ema'].iloc[-1]
            if gap > 0.7:
                return 3
            elif gap > 0.3:
                return 2
        return 1

    # Cap by $1000 max spend
    max_qty_by_price = int(1000 // price)
    scaled_qty = get_strategy_qty()
    qty = max(1, min(scaled_qty, max_qty_by_price))

    if symbol in executed_trades:
        print(f"Already traded {symbol} today. Skipping further trades.")
        return

    held_qty = int(positions.get(symbol, 0))

    # SELL FIRST if held
    if held_qty > 0:
        print(f"SELL {held_qty} of {symbol} at ${price:.2f} ({strategy_name})")
        api.submit_order(
            symbol=symbol,
            qty=held_qty,
            side='sell',
            type='market',
            time_in_force='day'
        )
        executed_trades.add(symbol)
        return

    if signal == 'buy':
        print(f"BUY {qty} of {symbol} at ${price:.2f} ({strategy_name})")
        api.submit_order(
            symbol=symbol,
            qty=qty,
            side='buy',
            type='market',
            time_in_force='day'
        )
        executed_trades.add(symbol)
    else:
        print(f"HOLD for {symbol} ({strategy_name})")






def save_to_csv(symbol, df, strategy_name):
    filename = f"/home/ubuntu/Data5500_mycode/Final_Project/CSV_Storage/{symbol}_{strategy_name}.csv"
    df_to_save = df.copy()
    df_to_save.reset_index(inplace=True)
    df_to_save['timestamp'] = pd.to_datetime(df_to_save['timestamp'])

    if os.path.exists(filename):
        existing = pd.read_csv(filename)
        last_saved_time = pd.to_datetime(existing['timestamp'].max())
        new_rows = df_to_save[df_to_save['timestamp'] > last_saved_time]

        if new_rows.empty:
            print(f"No new rows for {symbol} - {strategy_name}, skipping save.")
            return  # Exit without saving if no new rows
        else:
            print(f"Appending {len(new_rows)} new rows to {filename}")
            new_rows.to_csv(filename, mode='a', index=False, header=False)

    else:
        print(f"Creating new file for {symbol} - {strategy_name}")
        df_to_save.to_csv(filename, index=False)




def run_all_strategies_and_trade(stocks):
    results = {}
    executed_trades = set()  # 🆕 Track which stocks were already traded

    for symbol in stocks:
        try:
            print(f"\nRunning strategies for {symbol}...")
            df = get_data_bars([symbol], '5Min', 20, 5).get(symbol)
            if df is None or df.empty:
                print(f"No data for {symbol}")
                continue

            results[symbol] = {}

            # 1. SMA Crossover
            sma = sma_crossover_strategy(symbol, df)
            execute_trade(symbol, sma, "sma_crossover", executed_trades)
            results[symbol]['sma_crossover'] = simulate_trades(symbol, sma)
            save_to_csv(symbol, sma, "sma_crossover")

            # 2. Mean Reversion
            mean = mean_reversion_strategy(symbol, df)
            execute_trade(symbol, mean, "mean_reversion", executed_trades)
            results[symbol]['mean_reversion'] = simulate_trades(symbol, mean)
            save_to_csv(symbol, mean, "mean_reversion")

            # 3. Bollinger Bands
            boll = bollinger_band_strategy(symbol, df)
            execute_trade(symbol, boll, "bollinger_bands", executed_trades)
            results[symbol]['bollinger_bands'] = simulate_trades(symbol, boll)
            save_to_csv(symbol, boll, "bollinger_bands")

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    # Save results as before...
    # (you already have the rest of this part good)


    # Find the best performing strategy
    best = {"stock": None, "strategy": None, "profit": -float("inf")}
    for stock, strat_dict in results.items():
        for strat, profit in strat_dict.items():
            if profit > best["profit"]:
                best = {"stock": stock, "strategy": strat, "profit": profit}

    # Attach best result to the main results
    results["summary"] = {
        "most_profitable_stock": best["stock"],
        "most_profitable_strategy": best["strategy"],
        "max_profit": round(best["profit"], 2)
    }

    # Save to results.json (now includes summary)
    with open("/home/ubuntu/Data5500_mycode/Final_Project/results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("BEST STRATEGY:")
    print(f"{best['strategy']} on {best['stock']} made ${best['profit']:.2f}")


    print("BEST STRATEGY:")
    print(f"{best['strategy']} on {best['stock']} made ${best['profit']:.2f}")


run_all_strategies_and_trade(stocks)
open_orders = api.list_orders(status='open')
for order in open_orders:
    print(order.symbol, order.side, order.qty, order.status)

