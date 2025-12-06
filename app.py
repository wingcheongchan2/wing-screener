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
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- J Law 專用圖表函數 ---
def plot_jlaw_chart(ticker):
    # 1. 下載個股數據 (1年)
    stock_df = yf.download(ticker, period="1y", interval="1d", progress=False)
    
    # 2. 下載 S&P 500 數據 (用黎計 RS 線)
    spy_df = yf.download("SPY", period="1y", interval="1d", progress=False)
    
    if stock_df.empty:
        st.error(f"無法下載 {ticker} 數據")
        return

    # 3. 計算 4 大均線 (J Law 關鍵)
    stock_df['MA10'] = stock_df['Close'].rolling(window=10).mean()
    stock_df['MA20'] = stock_df['Close'].rolling(window=20).mean()
    stock_df['MA50'] = stock_df['Close'].rolling(window=50).mean()
    stock_df['MA200'] = stock_df['Close'].rolling(window=200).mean()

    # 4. 計算 RS Line (個股收市價 / SPY收市價) * 100
    # 注意：要確保 index 對齊
    common_index = stock_df.index.intersection(spy_df.index)
    rs_line = (stock_df.loc[common_index]['Close'] / spy_df.loc[common_index]['Close']) * 100
    
    # 5. 建立圖表 (兩個區域：上面係股價，下面係 RS 線)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, row_heights=[0.7, 0.3],
                        subplot_titles=(f"{ticker} 價格趨勢 (多頭排列監測)", "RS 強度線 (vs S&P 500)"))

    # --- 上半部：K線 + 均線 ---
    # K線
    fig.add_trace(go.Candlestick(x=stock_df.index,
                                 open=stock_df['Open'], high=stock_df['High'],
                                 low=stock_df['Low'], close=stock_df['Close'],
                                 name="股價"), row=1, col=1)
    
    # J Law 4條均線 (顏色參考常見設定)
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['MA10'], 
                             line=dict(color='green', width=1.5), name="10 MA (短期)"), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['MA20'], 
                             line=dict(color='yellow', width=1.5), name="20 MA (支撐)"), row=1, col=1)

    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['MA50'], 
                             line=dict(color='orange', width=2), name="50 MA (中期)"), row=1, col=1)

    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['MA200'], 
                             line=dict(color='red', width=2), name="200 MA (長期)"), row=1, col=1)

    # --- 下半部：RS Line ---
    fig.add_trace(go.Scatter(x=rs_line.index, y=rs_line, 
                             line=dict(color='cyan', width=2), name="RS Line"), row=2, col=1)

    # 設定版面樣式
    fig.update_layout(
        height=700,
        template="plotly_dark", # 黑底專業感
        xaxis_rangeslider_visible=False,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

# --- 整合到 UI ---
# 請將這段 Code 放喺你顯示完 Table 之後
st.divider()
st.header("📊 J Law 圖表分析")

# 假設你有一個變數叫 tickers 儲存咗股票名單 (如果你用上面的 scan result，可以直接用 scanned_tickers)
# 這裡我們做一個 Demo 下拉選單
if 'tickers' in locals() and len(tickers) > 0:
    selected_stock = st.selectbox("選擇要分析的股票：", tickers)
    
    if st.button("查看圖表"):
        with st.spinner(f"正在繪製 {selected_stock} 的 J Law 分析圖..."):
            plot_jlaw_chart(selected_stock)
            
            # 文字分析提示
            st.info("""
            **🧐 J Law 圖表檢查清單：**
            1. **均線排列**：是否 股價 > 10MA > 20MA > 50MA > 200MA？
            2. **RS 線 (下圖)**：藍色線是否**正在向上**？(代表跑贏大市)
            3. **回調機會**：股價是否回調到 **10MA (綠色)** 或 **20MA (黃色)** 附近？
            """)
else:
    st.warning("請先在側邊欄選擇來源並掃描股票。")
