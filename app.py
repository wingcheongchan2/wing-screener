import streamlit as st
import pandas as pd
import requests
from io import StringIO
from tradingview_ta import TA_Handler, Interval, Exchange

# --- 1. 獲取股票名單 (跟剛才一樣，用 Wikipedia) ---
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

# --- 2. 核心：向 TradingView 查詢數據 ---
def get_tv_analysis(ticker):
    try:
        # 建立 TradingView 查詢處理器
        handler = TA_Handler(
            symbol=ticker,
            screener="america",       # 美股
            exchange="NASDAQ",        # 交易所
            interval=Interval.INTERVAL_1_DAY # 日線圖
        )
        analysis = handler.get_analysis()
        return analysis
    except:
        return None

# --- UI 部分 ---
st.title("🚀 TradingView 自動分析器")
st.write("此工具使用 TradingView 的技術指標數據進行掃描。")

if st.button("開始掃描 Nasdaq 100 (尋找 Strong Buy)"):
    tickers = get_nasdaq100()
    
    if not tickers:
        st.error("無法獲取名單")
    else:
        st.info(f"找到 {len(tickers)} 隻股票，正在向 TradingView 查詢... (需時約 1-2 分鐘)")
        
        results = []
        progress_bar = st.progress(0)
        
        # 開始逐隻掃描
        for i, ticker in enumerate(tickers):
            # 更新進度條
            progress_bar.progress((i + 1) / len(tickers))
            
            # 獲取 TradingView 數據
            analysis = get_tv_analysis(ticker)
            
            if analysis:
                # 獲取總結評級 (BUY, SELL, STRONG_BUY, NEUTRAL)
                recommendation = analysis.summary['RECOMMENDATION']
                rsi = analysis.indicators['RSI']
                close = analysis.indicators['close']
                sma50 = analysis.indicators['SMA50']
                
                # 篩選條件：只要 "STRONG_BUY" 且 股價 > 50天線
                if recommendation == "STRONG_BUY" and close > sma50:
                    results.append({
                        "代號": ticker,
                        "現價": round(close, 2),
                        "TV評級": recommendation,
                        "RSI": round(rsi, 2),
                        "50 MA": round(sma50, 2)
                    })
        
        # 顯示結果
        st.success("掃描完成！")
        if results:
            df_results = pd.DataFrame(results)
            # 按 RSI 強度排序
            df_results = df_results.sort_values(by="RSI", ascending=False)
            st.dataframe(df_results)
        else:
            st.warning("沒有股票符合條件。")
