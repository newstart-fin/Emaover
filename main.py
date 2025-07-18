import time
import pandas as pd
import requests
import ta
from datetime import datetime

# === Configuration ===
SYMBOL = 'BTCUSDT'
INTERVAL = '5m'  # Options: '1m', '5m', '15m', '1h', '4h', '1d'
LIMIT = 200
SLEEP = 60  # seconds between checks

BINANCE_URL = f'https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval={INTERVAL}&limit={LIMIT}'

last_signal = None  # To prevent duplicate alerts


def fetch_ohlcv():
    response = requests.get(BINANCE_URL)
    if response.status_code != 200:
        print("Error fetching data:", response.status_code)
        return None

    data = response.json()
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df[['timestamp', 'close']]


def detect_crossover(df):
    global last_signal

    df['ema21'] = ta.trend.ema_indicator(df['close'], window=21)
    df['ema50'] = ta.trend.ema_indicator(df['close'], window=50)

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    # Detect crossover
    if previous['ema21'] < previous['ema50'] and latest['ema21'] > latest['ema50']:
        if last_signal != 'BUY':
            print(f"B 🔼 BUY Signal at {latest['timestamp']}")
            last_signal = 'BUY'
    elif previous['ema21'] > previous['ema50'] and latest['ema21'] < latest['ema50']:
        if last_signal != 'SELL':
            print(f"S 🔽 SELL Signal at {latest['timestamp']}")
            last_signal = 'SELL'


def main_loop():
    while True:
        df = fetch_ohlcv()
        if df is not None:
            detect_crossover(df)
        time.sleep(SLEEP)


if __name__ == "__main__":
    main_loop()
