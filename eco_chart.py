import streamlit as st
import requests
import time
import random
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta


@st.cache_data(show_spinner=False)
def fetch_yahoo_history(ticker, interval_option):
    now = datetime.now()
    if interval_option == "1분":
        from_day = now - timedelta(days=5)
        interval = "1m"
    elif  interval_option == "1년": 
        from_day = now - timedelta(days=365)
        interval = "1d"
    elif  interval_option == "5년": 
        from_day = now - timedelta(days=1825)
        interval = "1d"
    elif  interval_option == "10년": 
        from_day = now - timedelta(days=3650)
        interval = "1d"
    elif  interval_option == "20년": 
        from_day = now - timedelta(days=7300)
        interval = "1d"
    else : 
        from_day = datetime(1985, 1, 1)
        interval = "1d"
    period1 = int(time.mktime(from_day.timetuple()))
    period2 = int(time.mktime(now.timetuple()))

    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?"
        f"period1={period1}&period2={period2}&interval={interval}"
    )
    headers = {"User-Agent": "Mozilla/5.0"}
    for attempt in range(5):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            break
        elif response.status_code == 429:
            time.sleep(2 + random.random())
        else:
            response.raise_for_status()

    result = response.json()["chart"]["result"][0]
    timestamps = result["timestamp"]
    closes = result["indicators"]["quote"][0]["close"]
    prices = [
        (datetime.fromtimestamp(ts).replace(second=0, microsecond=0), close)
        for ts, close in zip(timestamps, closes)
        if close is not None
    ]
    return pd.DataFrame(prices, columns=["Date", "Price"]).set_index("Date")


def plot_chart(df, label, height,interval_option):
    recent_value = df["Price"].iloc[-1]
    recent_time = df.index[-1].strftime("%y.%m.%d %H:%M" if interval_option =="1분" else "%y.%m.%d")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index.strftime( "%m%d %H:%M" if interval_option =="1분" else "%Y-%m-%d"),
        y=df["Price"],
        mode='lines',
        name=label
    ))
    fig.update_layout(
        title=f"{label} {recent_value:.2f} ({recent_time})",
        title_font=dict(size=20),
        xaxis=dict(tickangle=90),
        shapes=[dict(
            type="line",
            xref="paper", x0=0, x1=1,
            yref="y", y0=recent_value, y1=recent_value,
            line=dict(color="red", width=0.5)
        )],
        height=height,
        margin=dict(t=60, b=100),
        dragmode=False
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def main():
    st.set_page_config(page_title="경제지표 실시간 차트", layout="wide")
    st.markdown('<h4>📈 경제지표 실시간 차트</h4>', unsafe_allow_html=True)
    st.markdown("")

    datasets = {
        "Dollar Index": "^NYICDX",
        "USD/KRW": "KRW=X",
        "JPY/KRW": "JPYKRW=X",
        "USD/JPY": "JPY=X",
        "USD/CNY": "CNY=X",
        "EUR/USD": "EURUSD=X",
        "VIX": "^VIX",
        "코스피": "^KS11",
        "코스닥": "^KQ11",
        "삼성전자": "005930.KS",
        "S&P500": "^GSPC",
        "NASDAQ": "^IXIC",
        "Apple": "AAPL",
        "CBOE 10Y T No": "^TNX",
        "Treasury 30Y": "^TYX",
        "IEF": "IEF",
        "TLT": "TLT",
        "Crude Oil": "CL=F",
        "Gold": "GC=F",
        "Silver": "SI=F",
        "Copper": "HG=F"
    }

    col1, col2 = st.columns([5, 1])
    with col1:
        selected = st.selectbox("📊지표선택", list(datasets.keys()))
    with col2:
        interval_option = st.selectbox("⏱️시간", ["1분", "1년", "5년", "10년", "20년","Max"])

    height_percent = st.slider("차트 높이 (기본: 100%)", min_value=50, max_value=150, value=100, step=5)
    chart_height = int(500 * height_percent / 100)

    with st.spinner(f"{selected} ({interval_option}) 데이터를 가져오는 중..."):
        df = fetch_yahoo_history(datasets[selected], interval_option)
        plot_chart(df, selected, chart_height, interval_option)

    st.caption("ⓒ 2025.1.30. 유행살이. All rights reserved.")


if __name__ == "__main__":
    main()
