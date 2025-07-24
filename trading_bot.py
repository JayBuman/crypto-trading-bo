import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import datetime

# RSI berechnen
def compute_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Strategie-Backtest
def backtest_strategy(data):
    capital = 1000  # Startkapital
    position = 0    # Coins
    capital_history = []

    for i in range(1, len(data)):
        row = data.iloc[i]
        price = row['Close']
        rsi = row['RSI']
        sma50 = row['SMA50']
        sma200 = row['SMA200']

        # NaNs überspringen
        if pd.isna(rsi) or pd.isna(sma50) or pd.isna(sma200):
            capital_history.append(capital + position * price)
            continue

        # Buy-Signal
        if rsi < 30 and sma50 > sma200 and position == 0:
            buy_amount = (capital * 0.1) / price
            position += buy_amount
            capital -= buy_amount * price
        # Sell-Signal
        elif rsi > 70 and position > 0:
            capital += position * price
            position = 0

        capital_history.append(capital + position * price)

    return capital_history

# GUI mit Streamlit
st.title("🧠 Krypto-Trading-Bot mit RSI + SMA Backtest")

symbol = st.text_input("Gib ein Symbol ein (z. B. BTC-USD, ETH-USD)", "BTC-USD")
start_date = st.date_input("Startdatum", datetime.date(2023, 1, 1))
end_date = st.date_input("Enddatum", datetime.date.today())

if st.button("Starte Backtest"):
    with st.spinner("Lade Daten..."):
        df = yf.download(symbol, start=start_date, end=end_date)
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['SMA200'] = df['Close'].rolling(window=200).mean()
        df['RSI'] = compute_rsi(df)

        st.subheader("Kursverlauf")
        st.line_chart(df[['Close', 'SMA50', 'SMA200']])

        st.subheader("RSI")
        st.line_chart(df[['RSI']])

        st.subheader("Kapitalentwicklung (Backtest)")
        capital_history = backtest_strategy(df)
        st.line_chart(capital_history)

        st.success(f"Backtest beendet. Endkapital: {capital_history[-1]:.2f} $")
