import streamlit as st
import pandas as pd
import ccxt
import datetime
import ta  # techn. Analyse (SMA, RSI)

# 📥 Funktion zum Laden historischer Daten von Binance
@st.cache_data
def fetch_binance_ohlcv(symbol='BTC/USDT', timeframe='1h', limit=500):
    binance = ccxt.binance()
    ohlcv = binance.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

# 🔄 Strategie: RSI < 30 = Buy, RSI > 70 = Sell + SMA-Kreuz
def backtest_strategy(df, rsi_period=14, sma1=50, sma2=200):
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=rsi_period).rsi()
    df['SMA50'] = df['Close'].rolling(window=sma1).mean()
    df['SMA200'] = df['Close'].rolling(window=sma2).mean()

    df.dropna(inplace=True)  # wichtig,
