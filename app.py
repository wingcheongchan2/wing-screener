import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import streamlit.components.v1 as components
from io import StringIO

# ==========================================
# 1. 系統設置
# ==========================================
st.set_page_config(page_title="J Law 冠軍操盤室 (全市場版)", layout="wide", page_icon="🚀")

st.title("🚀 J Law 冠軍操盤室 (全市場掃描 + 智能買點)")
st.markdown("""
**核心策略**：基於 M.E.T.S. 及 Pullback 策略，自動計算**買入觸發價**與**止損位**。
""")

# 初始化
if 'scan_results' not in st.session_state:
    st.session_state['scan_results'] = None

# ==========================================
# 2. 數據獲取 (S&P 500 & 納指)
# ==========================================
@st.cache_data
def get_sp500_tickers():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(requests.get(url, headers=headers).text)
        tickers = tables[0]['Symbol'].tolist()
        return [t.replace('.', '-') for t in tickers]
    except:
        # 後備名單
        return ["NVDA", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "TSLA", "AMD"]

@st.cache_data
def get_nasdaq100_tickers():
    # 這裡放一個靜態列表以保證速度和穩定性
    return [
        "NVDA", "MSFT", "AAPL", "AMZN", "META", "GOOGL", "GOOG", "TSLA", "AVGO", "COST",
        "AMD", "NFLX", "PEP", "LIN", "ADBE", "CSCO", "TMUS", "QCOM", "TXN", "INTU",
        "AMGN", "INTC", "ISRG", "HON", "AMAT", "BKNG", "SBUX", "MDLZ", "GILD", "ADP",
        "VRTX", "LRCX", "REGN", "ADI", "PANW", "MU", "SNPS", "KLAC", "CDNS", "CHTR",
        "CSX", "MAR", "PYPL", "ASML", "ORLY", "MNST", "NXPI", "ROP", "LULU", "AEP",
        "ADSK", "PDD", "WDAY", "FTNT", "KDP", "PAYX", "CTAS", "PCAR", "MCHP", "ODFL",
        "CRWD", "NET", "DDOG", "ZS", "MSTR", "COIN", "PLTR", "ARM", "SMCI", "UBER"
    ]

# ==========================================
# 3. 核心運算引擎 (計算買點邏輯)
# ==========================================
def analyze_stock(ticker, df):
    try:
        # 取得最新數據
        last_close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        last_high = df['High'].iloc[-1]
        last_low = df['Low'].iloc[-1]
        last_vol = df['Volume'].iloc[-1]
        avg_vol = df['Volume'].rolling(50).mean().iloc[-1]
        
        # 計算均線
        sma10 = df['Close'].rolling(10).mean().iloc[-1]
        sma20 = df['Close'].rolling(20).mean().iloc[-1]
        sma50 = df['Close'].rolling(50).mean().iloc[-1]
        sma200 = df['Close'].rolling(200).mean().iloc[-1]
        
        # 計算 RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]

        # --- 策略邏輯 ---
        signal = None
        setup_type = ""
        buy_trigger = 0
        stop_loss = 0

        # 1. 基礎趨勢：必須在 200MA 之上
        if last_close > sma200:
            
            # --- 拉回策略 (Pullback) ---
            # 條件：強勢股 (在50MA上) + 回調觸碰 10MA 或 20MA
            if last_close > sma50:
                dist_10 = abs(last_low - sma10) / sma10
                dist_20 = abs(last_low - sma20) / sma20
                
                # 判定：如果最低價觸碰到均線範圍 (1.5% 誤差內)
                if dist_10 <= 0.015:
                    setup_type = "🟢 10MA 強勢拉回"
                    # 買入點：突破昨日高點
                    buy_trigger = last_high + 0.05 
                    # 止損點：昨日低點下方
                    stop_loss = last_low - 0.05
                
                elif dist_20 <= 0.015:
                    setup_type = "🟡 20MA 標準拉回"
                    buy_trigger = last_high + 0.05
                    stop_loss = last_low - 0.05
            
            # --- 冠軍突破策略 (Breakout) ---
            # 條件：RSI 強 + 價格在所有均線之上
            if rsi > 65 and last_close > sma10 and last_close > sma20:
                setup_type = "🔥 冠軍動能強勢"
                buy_trigger = last_high + 0.10 # 突破續強
                stop_loss = sma20 # 跌破 20MA 止損

        if setup_type:
            return {
                "代號": ticker,
                "現價": round(last_close, 2),
                "策略": setup_type,
                "RSI": round(rsi, 1),
                "量能比": round(last_vol / avg_vol, 1), # <1 代表縮量
                "建議買入價": round(buy_trigger, 2),
                "建議止損價": round(stop_loss, 2),
                "潛在回報比": round((buy_trigger - stop_loss) * 3 + buy_trigger, 2) # 3R 目標
            }
    except:
        return None
    return None

# ==========================================
# 4. 顯示圖表與交易計劃
# ==========================================
def show_analysis_panel(ticker, row):
    # --- 1. 交易計劃卡片 ---
    st.markdown(f"### 📊 {ticker} 智能交易計劃")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("策略信號", row['策略'])
    c2.metric("🎯 觸發買入價 (Entry)", f"${row['建議買入價']}")
    c3.metric("🛑 止損位 (Stop)", f"${row['建議止損價']}")
    c4.metric("💰 目標價 (3R Target)", f"${row['潛在回報比']}")
    
    # 縮量提示
    if row['量能比'] < 0.8:
        st.caption(f"✅ **量能健康**：今日成交量僅為平均的 {row['量能比']}倍 (縮量回調)，這是一個好現象！")
    elif row['量能比'] > 1.5:
        st.caption(f"⚠️ **放量注意**：今日成交量較大 ({row['量能比']}倍)，請確認是買盤還是賣盤。")

    # --- 2. TradingView Widget ---
    html_code = f"""
    <div class="tradingview-widget-container">
      <div id="tradingview_chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "width": "100%",
        "height": 600,
        "symbol": "{ticker}",
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
# 5. 主界面邏輯
# ==========================================

# --- 側邊欄：來源選擇 ---
st.sidebar.header("🔍 1. 選擇搜尋範圍")
source_option = st.sidebar.radio(
    "股票池：",
    ["Nasdaq 100 (科技股)", "S&P 500 (全市場 - 較慢)", "自定義輸入"]
)

custom_list = []
if source_option == "自定義輸入":
    user_input = st.sidebar.text_area("輸入股票代號 (逗號分隔)", "PLTR, COIN, MSTR, AMD, SMCI")
    if user_input:
        custom_list = [x.strip().upper() for x in user_input.split(',')]

# --- 側邊欄：執行按鈕 ---
if st.sidebar.button("🚀 開始智能掃描", type="primary"):
    # 1. 確定名單
    target_tickers = []
    if source_option == "Nasdaq 100 (科技股)":
        target_tickers = get_nasdaq100_tickers()
    elif source_option == "S&P 500 (全市場 - 較慢)":
        with st.spinner("正在下載 S&P 500 名單..."):
            target_tickers = get_sp500_tickers()
    else:
        target_tickers = custom_list

    if not target_tickers:
        st.error("請輸入有效的股票代號")
    else:
        # 2. 批量下載數據 (YFinance)
        st.toast(f"正在分析 {len(target_tickers)} 隻股票，請稍候...", icon="⏳")
        results = []
        
        # 為了速度，我們分批次下載或者一次性下載
        # 這裡用一次性下載，然後本地 Loop 處理
        try:
            data = yf.download(target_tickers, period="1y", group_by='ticker', progress=False)
            
            progress_bar = st.progress(0)
            
            for i, ticker in enumerate(target_tickers):
                progress_bar.progress((i + 1) / len(target_tickers))
                
                # 處理單一 ticker 或多 ticker 的數據結構差異
                try:
                    if len(target_tickers) == 1:
                        df = data
                    else:
                        df = data[ticker]
                    
                    # 移除空值
                    df = df.dropna()
                    
                    if not df.empty and len(df) > 200:
                        res = analyze_stock(ticker, df)
                        if res:
                            results.append(res)
                except:
                    continue
            
            progress_bar.empty()
            
            # 3. 儲存結果
            if results:
                st.session_state['scan_results'] = pd.DataFrame(results)
            else:
                st.warning("沒有股票符合目前的 J Law 策略條件。")
                st.session_state['scan_results'] = pd.DataFrame()
                
        except Exception as e:
            st.error(f"發生錯誤: {e}")

# --- 主畫面：顯示結果 ---
col1, col2 = st.columns([4, 6])

with col1:
    st.subheader("📋 潛在機會清單")
    if st.session_state['scan_results'] is not None:
        df = st.session_state['scan_results']
        if not df.empty:
            # 排序：優先顯示拉回策略，然後按 RSI 排序
            df = df.sort_values(by="RSI", ascending=False)
            
            st.write(f"共發現 {len(df)} 個機會")
            st.dataframe(
                df[['代號', '現價', '策略', '建議買入價']], 
                use_container_width=True,
                hide_index=True
            )
            
            st.divider()
            target = st.selectbox("👇 選擇股票查看交易計劃：", df['代號'].tolist())
        else:
            st.info("暫無數據")
            target = None
    else:
        st.info("👈 請在左側設定並開始掃描")
        target = None

with col2:
    if target and st.session_state['scan_results'] is not None:
        # 獲取該行數據
        row_data = st.session_state['scan_results']
        row = row_data[row_data['代號'] == target].iloc[0]
        
        # 顯示分析面板
        show_analysis_panel(target, row)
