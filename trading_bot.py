# Speichere das als trading_bot.py auf https://share.streamlit.io (kostenlos online)

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("Crypto Trading Bot Simulator (RSI + SMA)")

# 1. Daten laden
@st.cache_data(ttl=3600)
def load_data(symbol="BTC-USD", period="1y", interval="1h"):
    df = yf.download(symbol, period=period, interval=interval)
    df = df.dropna()
    return df

df = load_data()

# 2. Indikatoren berechnen
def compute_indicators(data):
    close = data['Close']
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    sma_50 = close.rolling(window=50).mean()
    sma_200 = close.rolling(window=200).mean()
    data['RSI'] = rsi
    data['SMA50'] = sma_50
    data['SMA200'] = sma_200
    return data

df = compute_indicators(df)

# 3. Backtest-Funktion
def backtest_strategy(data, initial_capital=1000):
    capital = initial_capital
    position = 0  # BTC Menge
    capital_history = []

    for i in range(1, len(data)):
        row = data.iloc[i]
        price = row['Close']

        # Prüfen ob wichtige Indikatoren vorhanden sind (nicht NaN)
        if pd.isna(row['RSI']) or pd.isna(row['SMA50']) or pd.isna(row['SMA200']):
            capital_history.append(capital + position * price)
            continue

        # Signale: Buy wenn RSI < 30 und SMA50 > SMA200
        if row['RSI'] < 30 and row['SMA50'] > row['SMA200'] and position == 0:
            buy_amount = (capital * 0.1) / price
            position += buy_amount
            capital -= buy_amount * price
        # Sell wenn RSI > 70 und Position gehalten
        elif row['RSI'] > 70 and position > 0:
            capital += position * price
            position = 0

        total_value = capital + position * price
        capital_history.append(total_value)

    return capital_history


# 4. Backtest starten
if st.button("Backtest starten"):
    capital_history = backtest_strategy(df)
    st.write(f"Startkapital: 1000 USD")
    st.write(f"Endkapital: {capital_history[-1]:.2f} USD")
    st.write(f"Gewinn: {capital_history[-1] - 1000:.2f} USD")

    # Plot Kapitalverlauf
    fig, ax = plt.subplots()
    ax.plot(capital_history)
    ax.set_title("Kapitalverlauf im Backtest")
    ax.set_xlabel("Zeitschritte (Stunden)")
    ax.set_ylabel("Kapital (USD)")
    st.pyplot(fig)

# 5. Charts anzeigen
st.subheader("Kursverlauf mit Indikatoren")
fig2, ax2 = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

ax2[0].plot(df.index, df['Close'], label='Close')
ax2[0].plot(df.index, df['SMA50'], label='SMA 50')
ax2[0].plot(df.index, df['SMA200'], label='SMA 200')
ax2[0].set_ylabel("Preis (USD)")
ax2[0].legend()

ax2[1].plot(df.index, df['RSI'], label='RSI', color='orange')
ax2[1].axhline(30, color='green', linestyle='--')
ax2[1].axhline(70, color='red', linestyle='--')
ax2[1].set_ylabel("RSI")
ax2[1].legend()

ax2[2].plot(df.index, df['Close'], label='Close')
ax2[2].set_ylabel("Preis (USD)")
ax2[2].legend()

st.pyplot(fig2)
