import streamlit as st
import pandas as pd
import yfinance as yf
import streamlit.components.v1 as components
from tradingview_ta import TA_Handler, Interval, Exchange

# ==========================================
# 1. 系統設定與名單 (不依賴 Wikipedia)
# ==========================================
st.set_page_config(page_title="J Law 混合引擎選股器", layout="wide", page_icon="🚀")

st.title("🚀 J Law 冠軍操盤室 (混合引擎版)")
st.caption("引擎邏輯：優先使用 TradingView 數據 ➡️ 失敗自動轉用 Yahoo Finance 計算")

# --- 內置 Nasdaq 100 完整名單 (免去爬蟲錯誤) ---
# 這裡列出了主要的成分股，確保一定有數據
NASDAQ_100 = [
    "NVDA", "MSFT", "AAPL", "AMZN", "META", "GOOGL", "GOOG", "TSLA", "AVGO", "COST",
    "AMD", "NFLX", "PEP", "LIN", "ADBE", "CSCO", "TMUS", "QCOM", "TXN", "INTU",
    "AMGN", "INTC", "ISRG", "HON", "AMAT", "BKNG", "SBUX", "MDLZ", "GILD", "ADP",
    "VRTX", "LRCX", "REGN", "ADI", "PANW", "MU", "SNPS", "KLAC", "CDNS", "CHTR",
    "CSX", "MAR", "PYPL", "ASML", "ORLY", "MNST", "NXPI", "ROP", "LULU", "AEP",
    "ADSK", "PDD", "WDAY", "FTNT", "KDP", "PAYX", "CTAS", "PCAR", "MCHP", "ODFL",
    "ROST", "MRVL", "IDXX", "AIG", "FAST", "EXC", "VRSK", "CPRT", "BKR", "CTSH",
    "CEG", "XEL", "EA", "CSGP", "GEHC", "BIIB", "ON", "DXCM", "TEAM", "CDW",
    "GFS", "FANG", "DLTR", "ANSS", "WBD", "ILMN", "TTD", "WBA", "SIRI", "ZM",
    "CRWD", "NET", "DDOG", "ZS", "MSTR", "COIN", "PLTR", "ARM", "SMCI", "UBER"
]

# ==========================================
# 2. 核心功能：混合數據獲取 (Hybrid Fetch)
# ==========================================

# --- A. 嘗試用 TradingView 獲取 ---
def get_data_from_tv(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol,
            screener="america",
            exchange="NASDAQ",
            interval=Interval.INTERVAL_1_DAY
        )
        analysis = handler.get_analysis()
        if analysis:
            ind = analysis.indicators
            return {
                "close": ind.get("close"),
                "rsi": ind.get("RSI"),
                "sma10": ind.get("SMA10"),
                "sma20": ind.get("SMA20"),
                "sma50": ind.get("SMA50"),
                "sma150": ind.get("SMA100"), # TV API 默認可能沒有150，用100近似或需自定義，這裡暫用100
                "sma200": ind.get("SMA200"),
                "source": "TradingView"
            }
    except:
        return None
    return None

# --- B. 失敗後用 Yahoo Finance 獲取並計算 ---
def get_data_from_yf(symbol):
    try:
        # 下載過去 1.5 年數據以計算 200MA
        df = yf.download(symbol, period="2y", progress=False)
        if df.empty or len(df) < 200:
            return None
        
        # 處理多層索引 (如果有的話)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # 計算指標
        close = df['Close'].iloc[-1]
        
        # 計算 MA
        sma10 = df['Close'].rolling(window=10).mean().iloc[-1]
        sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        sma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        sma150 = df['Close'].rolling(window=150).mean().iloc[-1]
        sma200 = df['Close'].rolling(window=200).mean().iloc[-1]
        
        # 計算 RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
        
        return {
            "close": float(close),
            "rsi": float(rsi),
            "sma10": float(sma10),
            "sma20": float(sma20),
            "sma50": float(sma50),
            "sma150": float(sma150),
            "sma200": float(sma200),
            "source": "Yahoo Finance"
        }
    except:
        return None

# --- C. 混合調用函數 ---
def get_stock_data(symbol):
    # 1. 先試 TradingView
    data = get_data_from_tv(symbol)
    
    # 2. 如果 TV 失敗，轉用 Yahoo
    if data is None:
        data = get_data_from_yf(symbol)
        
    return data

# ==========================================
# 3. J Law 篩選邏輯
# ==========================================
def scan_jlaw_strategy(tickers, strategy):
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, ticker in enumerate(tickers):
        progress_bar.progress((i + 1) / len(tickers))
        status_text.text(f"分析中 ({i+1}/{len(tickers)}): {ticker}")
        
        # 獲取數據 (自動切換源)
        data = get_stock_data(ticker)
        
        if data:
            close = data['close']
            sma10 = data['sma10']
            sma20 = data['sma20']
            sma50 = data['sma50']
            sma150 = data['sma150']
            sma200 = data['sma200']
            rsi = data['rsi']
            
            # 防呆：確保所有指標都有數值
            if None in [close, sma10, sma20, sma50, sma200]:
                continue
                
            is_match = False
            signal = ""
            
            # --- 策略 1: 冠軍突破 (Strong Trend) ---
            if strategy == "冠軍模式 (Trend Template)":
                # 條件：多頭排列 (50 > 150 > 200) 且 股價 > 50MA
                trend_ok = (close > sma50) and (sma50 > sma150) and (sma150 > sma200)
                # 動能：RSI 強
                momentum_ok = rsi > 60
                
                if trend_ok and momentum_ok:
                    is_match = True
                    signal = "🔥 強勢多頭"

            # --- 策略 2: 拉回買入 (Pullback) ---
            elif strategy == "拉回買入 (Pullback)":
                # 大前提：長期趨勢必須向上 (股價 > 200MA)
                if close > sma200 and sma50 > sma200:
                    # 檢查 10MA 拉回 (誤差 2%)
                    if abs(close - sma10) / close <= 0.02:
                        is_match = True
                        signal = "🟢 10MA 支撐"
                    # 檢查 20MA 拉回 (誤差 2%)
                    elif abs(close - sma20) / close <= 0.02:
                        is_match = True
                        signal = "🟡 20MA 支撐"

            # --- 策略 3: 寬鬆觀察 ---
            elif strategy == "寬鬆模式 (測試用)":
                if close > sma200:
                    is_match = True
                    signal = "✅ 趨勢向上"

            if is_match:
                results.append({
                    "代號": ticker,
                    "現價": round(close, 2),
                    "RSI": round(rsi, 2),
                    "信號": signal,
                    "數據源": data['source'] # 顯示是用 TV 還是 Yahoo 找到的
                })
                
    progress_bar.empty()
    status_text.empty()
    return results

# ==========================================
# 4. 顯示 TradingView Widget (含 J Law 均線)
# ==========================================
def show_chart(symbol):
    html_code = f"""
    <div class="tradingview-widget-container">
      <div id="tradingview_chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "width": "100%",
        "height": 600,
        "symbol": "{symbol}",
        "interval": "D",
        "timezone": "Exchange",
        "theme": "dark",
        "style": "1",
        "locale": "zh_TW",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart",
        "studies": [
          {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 10 }}, "title": "10 MA" }},
          {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 20 }}, "title": "20 MA" }},
          {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 50 }}, "title": "50 MA" }},
          {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 200 }}, "title": "200 MA" }}
        ]
      }}
      );
      </script>
    </div>
    """
    components.html(html_code, height=600)

# ==========================================
# 5. UI 介面
# ==========================================

st.sidebar.header("🔍 掃描設定")
selected_strategy = st.sidebar.radio(
    "選擇 J Law 策略：",
    ["拉回買入 (Pullback)", "冠軍模式 (Trend Template)", "寬鬆模式 (測試用)"]
)

if st.sidebar.button("開始掃描", type="primary"):
    with st.spinner("正在啟動混合引擎掃描 Nasdaq 100..."):
        results = scan_jlaw_strategy(NASDAQ_100, selected_strategy)
        
        if results:
            df = pd.DataFrame(results)
            # 優先顯示數據源和 RSI
            st.session_state['scan_results'] = df
        else:
            st.warning("沒有股票符合條件。")
            st.session_state['scan_results'] = None

# 顯示結果區域
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader(f"📋 結果 ({selected_strategy})")
    if st.session_state.get('scan_results') is not None:
        df = st.session_state['scan_results']
        st.write(f"共找到 {len(df)} 隻股票")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.divider()
        target_stock = st.selectbox("👉 選擇股票查看圖表：", df['代號'].tolist())
    else:
        st.info("👈 請點擊左側按鈕開始")
        target_stock = None

with col2:
    st.subheader("📈 實時圖表")
    if target_stock:
        # 顯示是用哪個數據源找到的
        row = df[df['代號'] == target_stock].iloc[0]
        st.caption(f"數據來源: {row['數據源']} | 信號: {row['信號']}")
        show_chart(target_stock)
    else:
        st.write("請先掃描並選擇股票。")
