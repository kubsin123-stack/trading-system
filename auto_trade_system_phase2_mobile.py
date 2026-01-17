
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

st.set_page_config(page_title="Trading Decision System (Mobile)", layout="centered")

st.title("📱 Trading Decision System")

mobile_mode = st.checkbox("📱 Mobile Mode", value=True)

ticker = st.text_input("Stock Ticker (e.g. 2330 or AAPL)", "")

if ticker.isdigit():
    ticker = ticker + ".TW"

capital = st.number_input("Capital", value=120000, step=1000)
risk_pct = st.number_input("Risk per trade (%)", value=2.0, step=0.1)
entry_price = st.number_input("Entry Price", value=0.0, step=0.1)
stop_price = st.number_input("Stop Loss Price", value=0.0, step=0.1)
current_price = st.number_input("Current Price", value=0.0, step=0.1)

if ticker and entry_price > 0 and stop_price > 0:
    df = yf.download(ticker, period="6mo", interval="1d")

    if df.empty:
        st.error("No data found. Check ticker.")
        st.stop()

    df["EMA21"] = df["Close"].ewm(span=21).mean()
    df["EMA55"] = df["Close"].ewm(span=55).mean()
    df["EMA144"] = df["Close"].ewm(span=144).mean()

    latest = df.iloc[-1]

    trend_ok = latest["EMA144"] < latest["EMA55"] < latest["EMA21"]

    risk_per_share = abs(entry_price - stop_price)

    r1 = entry_price + risk_per_share
    r2 = entry_price + risk_per_share * 2
    r3 = entry_price + risk_per_share * 3

    if mobile_mode:
        st.markdown("---")
        st.markdown("## 📊 STATUS")

        if trend_ok:
            st.success("TREND OK")
        else:
            st.error("NO TRADE")

        st.markdown("## 🎯 R LEVELS")
        st.markdown(f"**1R:** {r1:.2f}")
        st.markdown(f"**2R:** {r2:.2f}")
        st.markdown(f"**3R:** {r3:.2f}")

        st.markdown("## 🧠 ACTION")

        if not trend_ok:
            st.error("NO TRADE")
        elif current_price >= r3:
            st.warning("REDUCE / TAKE PROFIT")
        elif current_price >= r2:
            st.info("MOVE STOP TO BREAKEVEN")
        elif current_price >= r1:
            st.success("ADD POSITION")
        else:
            st.info("WAIT")

    else:
        st.subheader("Trend")
        st.write("OK" if trend_ok else "Weak")

        st.subheader("R Levels")
        st.write(f"1R: {r1:.2f}")
        st.write(f"2R: {r2:.2f}")
        st.write(f"3R: {r3:.2f}")
