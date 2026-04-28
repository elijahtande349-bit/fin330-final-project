# ============================================================
# FIN 330 FINAL PROJECT — Stock Analytics & Portfolio Dashboard
# ============================================================
# This Streamlit app turns the Colab analysis into an
# interactive web dashboard. The user can pick any stock,
# build their own portfolio, and see live calculations.
#
# Every time the user changes an input, Streamlit re-runs
# the whole script from top to bottom — that's how it stays
# "live" and reactive.
# ============================================================

# --- IMPORTS ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# Must be the FIRST Streamlit command on the page.
# ============================================================
st.set_page_config(
    page_title="FIN 330 Final Project",
    page_icon="📈",
    layout="wide"
)

# ============================================================
# CUSTOM CSS STYLING — same polished look as Personal Finance app
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Mono&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.tip-box {
    background: #eff6ff;
    border-left: 4px solid #2563eb;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.25rem;
    margin-top: 1rem;
    font-size: 15px;
    color: #1e3a5f;
    line-height: 1.7;
}

.recommend-box {
    background: #f0fdf4;
    border-left: 4px solid #16a34a;
    border-radius: 0 8px 8px 0;
    padding: 1.25rem 1.5rem;
    margin-top: 1rem;
    font-size: 22px;
    font-weight: 600;
    color: #14532d;
    text-align: center;
}
.recommend-box.sell { background: #fef2f2; border-left-color: #dc2626; color: #7f1d1d; }
.recommend-box.hold { background: #fefce8; border-left-color: #ca8a04; color: #713f12; }

[data-testid="stMetric"] {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem 1.25rem;
}

.section-intro {
    font-size: 16px;
    color: #475569;
    margin-bottom: 1.5rem;
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def format_currency(value):
    return f"${value:,.2f}"

def format_pct(value):
    return f"{value:.2f}%"

# ============================================================
# APP TITLE & TABS
# ============================================================
st.title("📈 FIN 330 Final Project")
st.markdown("*Stock Analytics & Portfolio Dashboard — built with Python & Streamlit.*")

tab1, tab2, tab3 = st.tabs([
    "📊 Stock Analysis",
    "💼 Portfolio Dashboard",
    "📉 Risk Metrics"
])

# ============================================================
# TAB 1: INDIVIDUAL STOCK ANALYSIS
# ============================================================
with tab1:
    st.header("Individual Stock Analysis")
    st.markdown("""
    <p class="section-intro">
        Pick any stock ticker. The app pulls live price data from Yahoo Finance,
        calculates moving averages, Bollinger Bands, RSI, and volatility, and gives
        you a simple Buy / Sell / Hold recommendation.
    </p>
    """, unsafe_allow_html=True)

    # --- USER INPUTS ---
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input("Stock ticker", "AAPL").upper()
    with col2:
        period = st.selectbox("Time period", ["3mo", "6mo", "1y", "2y", "5y"], index=1)

    # --- DOWNLOAD DATA ---
    data = yf.download(ticker, period=period, auto_adjust=False)

    if data.empty:
        st.error(f"No data found for '{ticker}'. Please check the ticker.")
    else:
        st.success(f"Data successfully loaded for {ticker}")

        close = data["Close"].squeeze()

        # --- MOVING AVERAGES + BOLLINGER BANDS ---
        data["MA20"] = data["Close"].rolling(20).mean()
        data["MA50"] = data["Close"].rolling(50).mean()
        data["Upper"] = data["MA20"] + 2 * data["Close"].rolling(20).std()
        data["Lower"] = data["MA20"] - 2 * data["Close"].rolling(20).std()

        st.subheader("Price, Moving Averages & Bollinger Bands")
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        ax1.plot(data["Close"], label="Price")
        ax1.plot(data["MA20"], label="20-Day MA")
        ax1.plot(data["MA50"], label="50-Day MA")
        ax1.plot(data["Upper"], label="Upper Band", linestyle="--", color="gray")
        ax1.plot(data["Lower"], label="Lower Band", linestyle="--", color="gray")
        ax1.fill_between(data.index, data["Upper"].squeeze(), data["Lower"].squeeze(), alpha=0.1, color="gray")
        ax1.legend()
        ax1.set_title(f"{ticker} - Price, Moving Averages & Bollinger Bands")
        st.pyplot(fig1)

        # --- TREND METRICS ---
        current_price = close.iloc[-1]
        ma_20 = close.iloc[-20:].mean()
        ma_50 = close.iloc[-50:].mean()

        if current_price > ma_20 and ma_20 > ma_50:
            trend = "Strong Uptrend"
        elif current_price < ma_20 and ma_20 < ma_50:
            trend = "Strong Downtrend"
        else:
            trend = "Mixed Trend"

        st.subheader("Trend Snapshot")
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Current Price", format_currency(current_price))
        with m2: st.metric("20-Day MA", format_currency(ma_20))
        with m3: st.metric("50-Day MA", format_currency(ma_50))
        with m4: st.metric("Trend", trend)

        # --- RSI ---
        delta = close.diff()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)
        avg_gain = gains.rolling(14).mean()
        avg_loss = losses.rolling(14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]

        if current_rsi > 70:
            rsi_signal = "Overbought - Possible Sell Signal"
        elif current_rsi < 30:
            rsi_signal = "Oversold - Possible Buy Signal"
        else:
            rsi_signal = "Neutral"

        st.subheader("Relative Strength Index (RSI)")
        fig2, ax2 = plt.subplots(figsize=(10, 3.5))
        ax2.plot(rsi, label="RSI", color="purple")
        ax2.axhline(70, color="red", linestyle="--", label="Overbought (70)")
        ax2.axhline(30, color="green", linestyle="--", label="Oversold (30)")
        ax2.set_title(f"{ticker} - RSI Over Time")
        ax2.set_ylabel("RSI")
        ax2.legend()
        st.pyplot(fig2)

        r1, r2 = st.columns(2)
        with r1: st.metric("Current RSI", f"{current_rsi:.2f}")
        with r2: st.metric("RSI Signal", rsi_signal)

        # --- VOLATILITY ---
        daily_returns = close.pct_change()
        volatility = daily_returns.rolling(20).std().iloc[-1] * np.sqrt(252) * 100
        rolling_vol = daily_returns.rolling(20).std() * np.sqrt(252) * 100

        if volatility > 40:
            vol_level = "High Volatility"
        elif volatility > 25:
            vol_level = "Medium Volatility"
        else:
            vol_level = "Low Volatility"

        st.subheader("Annualized Volatility")
        fig3, ax3 = plt.subplots(figsize=(10, 3.5))
        ax3.plot(rolling_vol, color="orange")
        ax3.set_title(f"{ticker} - 20-Day Rolling Annualized Volatility")
        ax3.set_ylabel("Volatility (%)")
        st.pyplot(fig3)

        v1, v2 = st.columns(2)
        with v1: st.metric("Current Volatility", format_pct(volatility))
        with v2: st.metric("Volatility Level", vol_level)

        # --- FINAL RECOMMENDATION ---
        if trend == "Strong Uptrend" and rsi_signal == "Neutral":
            recommendation = "BUY"
            box_class = "recommend-box"
        elif trend == "Strong Downtrend" or rsi_signal == "Overbought - Possible Sell Signal":
            recommendation = "SELL"
            box_class = "recommend-box sell"
        else:
            recommendation = "HOLD"
            box_class = "recommend-box hold"

        st.subheader("Final Recommendation")
        st.markdown(f'<div class="{box_class}">Recommendation: {recommendation}</div>',
                    unsafe_allow_html=True)

        st.markdown(f"""
        <div class="tip-box">
            <strong>What this means:</strong><br><br>
            <strong>Trend:</strong> {trend}<br>
            <strong>RSI Signal:</strong> {rsi_signal}<br>
            <strong>Volatility:</strong> {vol_level} ({format_pct(volatility)})<br><br>
            This recommendation combines the trend (price vs. moving averages),
            momentum (RSI), and risk (volatility) into a single call. Use it as a
            starting point — not financial advice.
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# TAB 2: PORTFOLIO DASHBOARD
# ============================================================
with tab2:
    st.header("Portfolio Performance Dashboard")
    st.markdown("""
    <p class="section-intro">
        Build a 5-stock portfolio, set the weights, and see how it performed against
        the S&P 500 (SPY) over the past year. The dashboard shows individual returns,
        cumulative growth, allocation, and which stocks drove your performance.
    </p>
    """, unsafe_allow_html=True)

    # --- USER INPUTS ---
    st.subheader("Build Your Portfolio")
    default_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]

    cols = st.columns(5)
    tickers = []
    for i, c in enumerate(cols):
        with c:
            t = st.text_input(f"Ticker {i+1}", default_tickers[i]).upper()
            tickers.append(t)

    st.subheader("Set Weights (must add to 1.00)")
    wcols = st.columns(5)
    weights = []
    for i, c in enumerate(wcols):
        with c:
            w = st.number_input(f"{tickers[i]} weight", min_value=0.0, max_value=1.0,
                                value=0.20, step=0.05)
            weights.append(w)

    if round(sum(weights), 2) != 1.00:
        st.warning(f"Weights add to {sum(weights):.2f} — adjust to total 1.00 for accurate results.")
    else:
        st.success("Weights look good!")

    # --- DOWNLOAD DATA ---
    all_tickers = tickers + ["SPY"]
    raw = yf.download(all_tickers, period="1y", auto_adjust=False)
    prices = raw["Close"]

    if prices.empty or prices.isna().all().any():
        st.error("Could not load data for one or more tickers. Please check spelling.")
    else:
        # --- CALCULATIONS ---
        returns = prices.pct_change().dropna()
        stock_returns = returns[tickers]
        spy_returns = returns["SPY"]
        portfolio_returns = (stock_returns * weights).sum(axis=1)

        total_return = (1 + portfolio_returns).prod() - 1
        benchmark_return = (1 + spy_returns).prod() - 1

        days = len(portfolio_returns)
        annual_return = ((1 + total_return) ** (252 / days) - 1) * 100

        port_volatility = portfolio_returns.std() * np.sqrt(252) * 100
        sharpe = (portfolio_returns.mean() / portfolio_returns.std()) * np.sqrt(252)

        cumulative_portfolio = (1 + portfolio_returns).cumprod()
        cumulative_spy = (1 + spy_returns).cumprod()

        running_max = cumulative_portfolio.cummax()
        drawdown = (cumulative_portfolio - running_max) / running_max
        max_drawdown = drawdown.min() * 100

        covariance = np.cov(portfolio_returns, spy_returns)[0, 1]
        spy_variance = spy_returns.var()
        beta = covariance / spy_variance

        # --- HEADLINE METRICS ---
        st.subheader("Headline Performance")
        h1, h2, h3 = st.columns(3)
        with h1: st.metric("Portfolio Return", format_pct(total_return * 100))
        with h2: st.metric("Benchmark (SPY)", format_pct(benchmark_return * 100))
        with h3: st.metric("Outperformance", format_pct((total_return - benchmark_return) * 100))

        # --- INDIVIDUAL RETURNS ---
        st.subheader("Individual Stock Returns")
        ind_cols = st.columns(5)
        for i, c in enumerate(ind_cols):
            with c:
                stock_total = (1 + stock_returns[tickers[i]]).prod() - 1
                st.metric(tickers[i], format_pct(stock_total * 100))

        # --- PORTFOLIO vs SPY CHART ---
        st.subheader("Portfolio vs. SPY — Cumulative Return")
        fig4, ax4 = plt.subplots(figsize=(10, 5))
        ax4.plot(cumulative_portfolio, label="Our Portfolio")
        ax4.plot(cumulative_spy, label="SPY Benchmark")
        ax4.legend()
        ax4.set_title("Portfolio vs. SPY - 1 Year Cumulative Return")
        ax4.set_ylabel("Growth of $1")
        st.pyplot(fig4)

        # --- DRAWDOWN CHART ---
        st.subheader("Portfolio Drawdown Over Time")
        fig5, ax5 = plt.subplots(figsize=(10, 3.5))
        ax5.fill_between(drawdown.index, drawdown * 100, 0, color="red", alpha=0.3)
        ax5.plot(drawdown * 100, color="red")
        ax5.set_title("Drawdown (%)")
        ax5.set_ylabel("Drawdown (%)")
        st.pyplot(fig5)

        # --- ALLOCATION + CONTRIBUTION ---
        st.subheader("Allocation & Contribution")
        ac1, ac2 = st.columns(2)

        with ac1:
            st.markdown("**Portfolio Allocation**")
            fig6, ax6 = plt.subplots(figsize=(6, 6))
            ax6.pie(weights, labels=tickers, autopct="%1.1f%%", startangle=90)
            st.pyplot(fig6)

        with ac2:
            st.markdown("**Contribution to Return**")
            contributions = []
            for i, t in enumerate(tickers):
                stock_total = (1 + stock_returns[t]).prod() - 1
                contributions.append(weights[i] * stock_total * 100)

            fig7, ax7 = plt.subplots(figsize=(6, 6))
            colors = ["green" if c > 0 else "red" for c in contributions]
            ax7.bar(tickers, contributions, color=colors)
            ax7.axhline(0, color="black", linewidth=0.8)
            ax7.set_title("Each Stock's Contribution (%)")
            ax7.set_ylabel("Contribution (%)")
            st.pyplot(fig7)

        # Save metrics for tab 3
        st.session_state["metrics"] = {
            "total_return": total_return * 100,
            "annual_return": annual_return,
            "benchmark_return": benchmark_return * 100,
            "outperformance": (total_return - benchmark_return) * 100,
            "volatility": port_volatility,
            "sharpe": sharpe,
            "max_drawdown": max_drawdown,
            "beta": beta
        }

        st.markdown(f"""
        <div class="tip-box">
            <strong>What this means:</strong><br><br>
            Your portfolio returned <strong>{format_pct(total_return * 100)}</strong>
            vs SPY's <strong>{format_pct(benchmark_return * 100)}</strong> — an
            outperformance of <strong>{format_pct((total_return - benchmark_return) * 100)}</strong>.
            Use the Risk Metrics tab to see detailed risk-adjusted performance.
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# TAB 3: RISK METRICS
# ============================================================
with tab3:
    st.header("Risk-Adjusted Performance")
    st.markdown("""
    <p class="section-intro">
        Returns alone don't tell the full story. Professional investors evaluate
        portfolios using risk-adjusted metrics — measures that account for volatility,
        drawdowns, and how much the portfolio moves with the market.
    </p>
    """, unsafe_allow_html=True)

    if "metrics" not in st.session_state:
        st.info("Build your portfolio in the **Portfolio Dashboard** tab first to see risk metrics here.")
    else:
        m = st.session_state["metrics"]

        st.subheader("Return Metrics")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Total Return", format_pct(m["total_return"]))
        with c2: st.metric("Annualized (CAGR)", format_pct(m["annual_return"]))
        with c3: st.metric("Benchmark (SPY)", format_pct(m["benchmark_return"]))
        with c4: st.metric("Outperformance", format_pct(m["outperformance"]))

        st.subheader("Risk Metrics")
        r1, r2, r3, r4 = st.columns(4)
        with r1: st.metric("Volatility", format_pct(m["volatility"]))
        with r2: st.metric("Sharpe Ratio", f"{m['sharpe']:.2f}")
        with r3: st.metric("Max Drawdown", format_pct(m["max_drawdown"]))
        with r4: st.metric("Beta vs SPY", f"{m['beta']:.2f}")

        if m["beta"] > 1:
            beta_msg = "Your portfolio is <strong>more volatile</strong> than the market."
        elif m["beta"] < 1:
            beta_msg = "Your portfolio is <strong>less volatile</strong> than the market."
        else:
            beta_msg = "Your portfolio moves <strong>in line</strong> with the market."

        st.markdown(f"""
        <div class="tip-box">
            <strong>How to read these numbers:</strong><br><br>
            <strong>Sharpe Ratio</strong> — return per unit of risk. Above 1.0 is good, above 2.0 is excellent.<br>
            <strong>Max Drawdown</strong> — the worst peak-to-trough loss. Tells you the deepest hole the portfolio fell into.<br>
            <strong>Beta</strong> — sensitivity to the market. {beta_msg}<br>
            <strong>CAGR</strong> — annualized return, the most apples-to-apples way to compare investments over different time periods.
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption("Built with Python & Streamlit · FIN 330 Final Project · For educational purposes")


