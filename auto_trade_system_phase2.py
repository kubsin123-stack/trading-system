import streamlit as st
import pandas as pd
import numpy as np
import datetime
import yfinance as yf

st.set_page_config(page_title="Trading Decision System - Phase 2", layout="wide")
st.title("Trading Decision System - Phase 2")

ticker = st.sidebar.text_input("Ticker (e.g. AAPL or 2330.TW)", value="AAPL")
capital = st.sidebar.number_input("Capital", value=120000, step=1000)
risk_pct = st.sidebar.slider("Risk per trade (%)", 0.5, 5.0, 2.0) / 100

entry_price = st.sidebar.number_input("Initial entry price", value=0.0)
stop_price = st.sidebar.number_input("Stop loss price", value=0.0)
current_price = st.sidebar.number_input("Current price", value=0.0)

@st.cache_data
def load_data(ticker):
    df = yf.download(ticker, period="6mo", interval="1d")
    df.dropna(inplace=True)
    return df

df = load_data(ticker)

df["EMA21"] = df["Close"].ewm(span=21).mean()
df["EMA55"] = df["Close"].ewm(span=55).mean()
df["EMA144"] = df["Close"].ewm(span=144).mean()

ema_fast = df["Close"].ewm(span=12).mean()
ema_slow = df["Close"].ewm(span=26).mean()
df["MACD"] = ema_fast - ema_slow
df["MACD_signal"] = df["MACD"].ewm(span=9).mean()

low_min = df["Low"].rolling(9).min()
high_max = df["High"].rolling(9).max()
df["K"] = (df["Close"] - low_min) / (high_max - low_min) * 100
df["D"] = df["K"].rolling(3).mean()

latest = df.iloc[-1]

trend_ok = (float(latest["EMA144"]) < float(latest["EMA55"])) and (float(latest["EMA55"]) < float(latest["EMA21"]))
macd_ok = float(latest["MACD"]) > float(latest["MACD_signal"])
kdj_ok = float(latest["K"]) > float(latest["D"])

st.subheader("Market status")

c1, c2, c3 = st.columns(3)
c1.metric("Trend", "OK" if trend_ok else "Weak")
c2.metric("MACD", "Golden" if macd_ok else "Negative")
c3.metric("KDJ", "Golden" if kdj_ok else "Negative")

if entry_price > 0 and stop_price > 0 and entry_price != stop_price:
    risk_per_share = abs(entry_price - stop_price)
    r1 = entry_price + risk_per_share
    r2 = entry_price + risk_per_share * 2
    r3 = entry_price + risk_per_share * 3

    st.subheader("R levels")
    st.write("1R:", round(r1, 2))
    st.write("2R:", round(r2, 2))
    st.write("3R:", round(r3, 2))

    st.subheader("Position management")

    if current_price >= r1 and trend_ok and macd_ok:
        st.success("Price >= 1R: Add position allowed")
    if current_price >= r2:
        st.success("Price >= 2R: Move stop loss to breakeven")
    if current_price >= r3:
        st.success("Price >= 3R: Consider trailing stop or partial exit")

    if not trend_ok or not macd_ok:
        st.warning("Trend weakening: avoid adding, consider reducing position")

st.subheader("Trade log")

if "trades" not in st.session_state:
    st.session_state.trades = []

if st.button("Add trade record"):
    st.session_state.trades.append({
        "Time": datetime.datetime.now(),
        "Entry": entry_price,
        "Stop": stop_price,
        "Current": current_price
    })

if st.session_state.trades:
    df_log = pd.DataFrame(st.session_state.trades)
    st.dataframe(df_log)
