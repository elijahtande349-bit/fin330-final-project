import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import streamlit as st

st.title("FIN 330 Final Project - Stock Analytics & Portfolio Dashboard")

"""# PART 1: Individual Stock Analysis"""
ticker = "AAPL"
data = yf.download(ticker, period="6mo", auto_adjust=False)

# Calculate Moving Averages
data["MA20"] = data["Close"].rolling(20).mean()
data["MA50"] = data["Close"].rolling(50).mean()

# Plot price vs. moving averages
fig1, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot(data["Close"], label="Price")
ax1.plot(data["MA20"], label="20-Day MA")
ax1.plot(data["MA50"], label="50-Day MA")
ax1.legend()
ax1.set_title(f"{ticker} - Price and Moving Averages")
st.pyplot(fig1)

# Metrics calculation
close = data["Close"].squeeze()
current_price = close.iloc[-1]
ma_20 = data["MA20"].iloc[-1]
ma_50 = data["MA50"].iloc[-1]

st.metric(label="Current Price", value=f"${current_price:.2f}")
st.write(f"**20-Day MA:** ${ma_20:.2f} | **50-Day MA:** ${ma_50:.2f}")

# Trend logic
if current_price > ma_20 and current_price > ma_50:
    trend = "Strong Uptrend"
elif current_price < ma_20 and current_price < ma_50:
    trend = "Strong Downtrend"
else:
    trend = "Mixed Trend"

# RSI Calculation
delta = close.diff()
gains = delta.clip(lower=0)
losses = -delta.clip(upper=0)
avg_gain = gains.rolling(14).mean()
avg_loss = losses.rolling(14).mean()
rs = avg_gain / avg_loss
rsi = 100 - (100 / (1 + rs))
current_rsi = rsi.iloc[-1]

if current_rsi > 70:
    rsi_signal = "Overbought"
elif current_rsi < 30:
    rsi_signal = "Oversold"
else:
    rsi_signal = "Neutral"

# Volatility
daily_returns = close.pct_change()
volatility = daily_returns.rolling(20).std().iloc[-1] * np.sqrt(252) * 100
vol_level = "High" if volatility > 40 else "Medium" if volatility > 25 else "Low"

st.write(f"**Trend:** {trend} | **RSI:** {current_rsi:.2f} ({rsi_signal}) | **Volatility:** {volatility:.2f}% ({vol_level})")

"""# PART 2: Portfolio Performance Dashboard"""
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]
weights = [0.20, 0.20, 0.20, 0.20, 0.20]

all_tickers = tickers + ["SPY"]
raw = yf.download(all_tickers, period="1y", auto_adjust=False)
prices = raw["Close"]
returns = prices.pct_change().dropna()

stock_returns = returns[tickers]
spy_returns = returns["SPY"]
portfolio_returns = (stock_returns * weights).sum(axis=1)

total_return = (1 + portfolio_returns).prod() - 1
benchmark_return = (1 + spy_returns).prod() - 1
sharpe = (portfolio_returns.mean() / portfolio_returns.std()) * np.sqrt(252)

# Display Portfolio Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Portfolio Return", f"{total_return * 100:.2f}%")
col2.metric("Benchmark (SPY)", f"{benchmark_return * 100:.2f}%")
col3.metric("Sharpe Ratio", f"{sharpe:.2f}")

# Plot Portfolio vs SPY
cumulative_portfolio = (1 + portfolio_returns).cumprod()
cumulative_spy = (1 + spy_returns).cumprod()

fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.plot(cumulative_portfolio, label="My Portfolio")
ax2.plot(cumulative_spy, label="SPY Benchmark")
ax2.legend()
ax2.set_title("Portfolio vs. SPY - 1 Year Cumulative Return")
st.pyplot(fig2)
