import streamlit as st
import pandas as pd
import requests
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import StringIO
from tradingview_ta import TA_Handler, Interval, Exchange

# ==========================================
# 1. 設定頁面
# ==========================================
st.set_page_config(page_title="J Law 選股神器", layout="wide")
st.title("🚀 J Law (USIC 冠軍) 智能選股 & 圖表分析")

# 初始化 Session State (用黎記住掃描結果)
if 'scan_results' not in st.session_state:
    st.session_state['scan_results'] = None

# ==========================================
# 2. 核心功能函數
# ==========================================

# --- 獲取 Nasdaq 100 名單 ---
@st.cache_data
def get_nasdaq100():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
        response = requests.get(url, headers=headers)
        tables = pd.read_html(StringIO(response.text))
        for table in tables:
            if 'Ticker' in table.columns:
                return table['Ticker'].tolist()
        return []
    except:
        return []

# --- TradingView 數據查詢 ---
def get_tv_analysis(ticker):
    try:
        handler = TA_Handler(
            symbol=ticker,
            screener="america",
            exchange="NASDAQ",
            interval=Interval.INTERVAL_1_DAY
        )
        return handler.get_analysis()
    except:
        return None

# --- 繪畫 J Law 圖表 (K線 + 4條均線 + RS Line) ---
def plot_jlaw_chart(ticker):
    # 下載個股與大盤數據
    stock_df = yf.download(ticker, period="1y", interval="1d", progress=False)
    spy_df = yf.download("SPY", period="1y", interval="1d", progress=False)
    
    if stock_df.empty or spy_df.empty:
        st.error(f"無法下載 {ticker} 的數據，請稍後再試。")
        return

    # 計算均線
    stock_df['MA10'] = stock_df['Close'].rolling(window=10).mean()
    stock_df['MA20'] = stock_df['Close'].rolling(window=20).mean()
    stock_df['MA50'] = stock_df['Close'].rolling(window=50).mean()
    stock_df['MA200'] = stock_df['Close'].rolling(window=200).mean()

    # 計算 RS Line
    common_index = stock_df.index.intersection(spy_df.index)
    rs_line = (stock_df.loc[common_index]['Close'] / spy_df.loc[common_index]['Close']) * 100

    # 建立圖表
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, row_heights=[0.7, 0.3],
                        subplot_titles=(f"{ticker} 價格趨勢 (多頭排列)", "RS 強度線 (vs S&P 500)"))

    # 上半部：K線
    fig.add_trace(go.Candlestick(x=stock_df.index,
                                 open=stock_df['Open'], high=stock_df['High'],
                                 low=stock_df['Low'], close=stock_df['Close'],
                                 name="K線"), row=1, col=1)
    
    # 上半部：均線
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['MA10'], line=dict(color='green', width=1), name="10 MA"), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['MA20'], line=dict(color='yellow', width=1), name="20 MA"), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['MA50'], line=dict(color='orange', width=2), name="50 MA"), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['MA200'], line=dict(color='red', width=2), name="200 MA"), row=1, col=1)

    # 下半部：RS Line
    fig.add_trace(go.Scatter(x=rs_line.index, y=rs_line, line=dict(color='cyan', width=2), name="RS Line"), row=2, col=1)

    fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 3. 主介面邏輯
# ==========================================

# --- 步驟 1: 掃描按鈕 ---
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("🔍 開始掃描 Nasdaq 100 (Strong Buy)", type="primary"):
        tickers = get_nasdaq100()
        if not tickers:
            st.error("無法獲取名單")
        else:
            status_text = st.empty()
            progress_bar = st.progress(0)
            results = []
            
            # 為了示範，這裡只掃描前 30 隻，以免太耐 (你可以自己改 range)
            scan_limit = 30 
            target_list = tickers[:scan_limit]
            
            for i, ticker in enumerate(target_list):
                status_text.text(f"正在分析: {ticker} ({i+1}/{len(target_list)})")
                progress_bar.progress((i + 1) / len(target_list))
                
                analysis = get_tv_analysis(ticker)
                if analysis:
                    rec = analysis.summary['RECOMMENDATION']
                    close = analysis.indicators['close']
                    sma50 = analysis.indicators['SMA50']
                    rsi = analysis.indicators['RSI']
                    
                    # 篩選邏輯：Strong Buy + 價格 > 50天線
                    if rec == "STRONG_BUY" and close > sma50:
                        results.append({
                            "代號": ticker,
                            "現價": round(close, 2),
                            "RSI": round(rsi, 2),
                            "TV評級": rec
                        })
            
            status_text.text("掃描完成！")
            progress_bar.empty()
            
            # 將結果存入 Session State
            if results:
                df = pd.DataFrame(results).sort_values(by="RSI", ascending=False)
                st.session_state['scan_results'] = df
            else:
