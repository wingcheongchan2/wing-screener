import streamlit as st
import yfinance as yf
import pandas as pd
import requests 
import streamlit.components.v1 as components
from datetime import datetime

# ==========================================
# 1. 系統配置 & CSS (視覺優化)
# ==========================================
st.set_page_config(page_title="J Law Alpha Station", layout="wide", page_icon="🦅")

# TSLA 背景圖 (Unsplash 高清)
TSLA_BG = "https://images.unsplash.com/photo-1560958089-b8a1929cea89?q=80&w=2071&auto=format&fit=crop"

def inject_css(mode):
    # 預設 CSS (適用於掃描 & 觀察區)
    base_style = """
    <style>
        .stApp {
            background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
            color: #E0E0E0;
        }
        section[data-testid="stSidebar"] {
            background-color: #050505;
            border-right: 1px solid #333;
        }
        /* 列表按鈕優化 */
        div.stRadio > div[role="radiogroup"] > label {
            background: #111;
            border: 1px solid #333;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 5px;
            display: block;
            transition: 0.2s;
        }
        div.stRadio > div[role="radiogroup"] > label:hover {
            border-color: #00E676;
            background: #1a1a1a;
        }
        /* 選中狀態 */
        div.stRadio > div[role="radiogroup"] > label[data-checked="true"] {
            background: linear-gradient(90deg, #00C853, #009624);
            color: white !important;
            border: none;
        }
        
        /* 數據卡片 */
        .metric-card {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            border: 1px solid #333;
        }
        
        /* StockTwits 卡片 */
        .twit-card {
            background: rgba(20,20,20,0.8);
            border-left: 3px solid #304FFE;
            padding: 10px; margin-bottom: 10px; border-radius: 5px;
        }
    </style>
    """
    
    # TSLA 專屬背景 CSS
    tsla_style = f"""
    <style>
        [data-testid="stAppViewContainer"] {{
            background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("{TSLA_BG}");
            background-size: cover;
            background-attachment: fixed;
        }}
        .stApp {{ background: transparent; }}
    </style>
    """
    
    if mode == "⚡ TSLA 戰情室 (Intel)":
        st.markdown(tsla_style + base_style, unsafe_allow_html=True)
    else:
        st.markdown(base_style, unsafe_allow_html=True)

# ==========================================
# 2. 核心分析邏輯 (恢復詳細計算)
# ==========================================
@st.cache_data
def get_tickers():
    return ["NVDA", "TSLA", "AMD", "PLTR", "COIN", "MSTR", "SMCI", "ARM", "HOOD", "AAPL", "MSFT", "AMZN", "META", "GOOGL"]

def analyze_stock_logic(ticker, df):
    """恢復 v2 版本的詳細分析逻辑"""
    try:
        if len(df) < 100: return None
        curr = df.iloc[-1]
        close = curr['Close']
        high = curr['High']
        low = curr['Low']
        
        # 均線
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        
        pattern = ""
        score = 0
        reasons = []
        
        # 1. 型態判斷
        dist_20 = (low - ma20) / ma20
        dist_10 = (low - ma10) / ma10
        
        if abs(dist_20) <= 0.03 and close > ma20:
            pattern = "🎾 Tennis Ball (20MA)"
            score = 90
            reasons.append(f"股價回測 20MA (${ma20:.2f}) 獲得支撐，呈現網球反彈行為。")
        elif abs(dist_10) <= 0.02 and close > ma10:
            pattern = "🔥 Power Trend (10MA)"
            score = 95
            reasons.append(f"股價沿著 10MA (${ma10:.2f}) 強勢整理，動能極強。")
        elif abs((low - ma50)/ma50) <= 0.03 and close > ma50:
            pattern = "🛡️ Defense (50MA)"
            score = 80
            reasons.append(f"回測 50MA 機構防線 (${ma50:.2f})。")
        else:
            return None # 過濾掉沒有型態的股票
            
        # 2. 計算交易計劃
        entry = high + (atr * 0.1) # 突破高點買入
        stop = low - (atr * 0.1)   # 跌破低點止損
        if entry <= stop: return None
        
        risk = entry - stop
        target = entry + (risk * 3) # 3R 目標
        
        return {
            "Symbol": ticker,
            "Pattern": pattern,
            "Score": score,
            "Close": close,
            "Entry": round(entry, 2),
            "Stop": round(stop, 2),
            "Target": round(target, 2),
            "Analysis": " ".join(reasons)
        }
    except: return None

# ==========================================
# 3. 顯示組件 (TradingView & 詳情卡)
# ==========================================
def display_full_analysis(row):
    """顯示完整的分析介面 (回復 v2 的佈局)"""
    
    # 1. 頂部分析文案
    st.markdown(f"### {row['Symbol']} - {row['Pattern']}")
    st.info(f"🤖 **J Law AI 分析**：{row['Analysis']}")
    
    # 2. 數據格 (使用 Streamlit 原生 Metric，美觀清晰)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("現價 (Price)", f"${row['Close']:.2f}")
    c2.metric("買入 (Entry)", f"${row['Entry']:.2f}", delta="Breakout")
    c3.metric("止損 (Stop)", f"${row['Stop']:.2f}", delta_color="inverse")
    c4.metric("目標 (3R)", f"${row['Target']:.2f}", delta_color="normal")
    
    st.write("---")
    
    # 3. TradingView K線圖 (Advanced Chart Widget)
    st.markdown("#### 📈 即時 K 線圖表")
    tv_html = f"""
    <div class="tradingview-widget-container" style="height:500px;width:100%">
      <div id="tv_{row['Symbol']}" style="height:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{row['Symbol']}",
        "interval": "D",
        "timezone": "Exchange",
        "theme": "dark",
        "style": "1",
        "locale": "zh_TW",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "tv_{row['Symbol']}",
        "studies": [ "MASimple@tv-basicstudies", "MASimple@tv-basicstudies", "MASimple@tv-basicstudies" ],
        "studies_overrides": {{
            "MASimple@tv-basicstudies.length": 10,
            "MASimple@tv-basicstudies.length": 20,
            "MASimple@tv-basicstudies.length": 50
        }}
      }});
      </script>
    </div>
    """
    components.html(tv_html, height=510)

def get_stocktwits(symbol):
    try:
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=3)
        return r.json().get('messages', [])
    except: return []

# ==========================================
# 4. 主程式邏輯
# ==========================================

# 狀態初始化
if 'scan_data' not in st.session_state: st.session_state['scan_data'] = None
if 'watchlist' not in st.session_state: st.session_state['watchlist'] = ["TSLA", "NVDA", "PLTR"]

with st.sidebar:
    st.markdown("## 🦅 COMMAND CENTER")
    mode = st.radio("模式選擇", ["🚀 自動掃描 (Scanner)", "👀 觀察名單 (Watchlist)", "⚡ TSLA 戰情室 (Intel)"])
    
    st.markdown("---")
    
    if mode == "🚀 自動掃描 (Scanner)":
        if st.button("🔥 啟動全市場掃描", use_container_width=True):
            with st.spinner("正在計算 Alpha 信號..."):
                ts = get_tickers()
                data = yf.download(ts, period="6mo", group_by='ticker', threads=True, progress=False)
                res = []
                for t in ts:
                    try:
                        df = data[t].dropna() if len(ts) > 1 else data
                        r = analyze_stock_logic(t, df)
                        if r: res.append(r)
                    except: continue
                
                if res:
                    st.session_state['scan_data'] = pd.DataFrame(res).sort_values('Score', ascending=False)
                else:
                    st.session_state['scan_data'] = pd.DataFrame()

# 注入 CSS
inject_css(mode)

st.title("🦅 J Law Alpha Station")

# --- 模式 1: 掃描器 (回復左右佈局) ---
if mode == "🚀 自動掃描 (Scanner)":
    df = st.session_state['scan_data']
    
    if df is None:
        st.info("👈 請點擊左側 [啟動全市場掃描] 開始。")
    elif df.empty:
        st.warning("⚠️ 目前市場波動大，未發現符合 J Law 標準的完美 Setup。")
    else:
        # 這裡改用 st.columns 實現左右佈局，解決「選擇不方便」的問題
        col_list, col_detail = st.columns([1, 3])
        
        with col_list:
            st.markdown("### 📋 訊號列表")
            # 使用 Radio 來做選擇列表，並自定義顯示格式
            selected_ticker = st.radio(
                "選擇股票：",
                options=df['Symbol'].tolist(),
                format_func=lambda x: f"{x}  |  {df[df['Symbol']==x]['Score'].values[0]}分",
                label_visibility="collapsed"
            )
            st.caption("🔥 95分: Power Trend")
            st.caption("🎾 90分: Tennis Ball")
        
        with col_detail:
            # 取出選中股票的資料行
            row = df[df['Symbol'] == selected_ticker].iloc[0]
            display_full_analysis(row)

# --- 模式 2: 觀察名單 (同樣使用左右佈局) ---
elif mode == "👀 觀察名單 (Watchlist)":
    col_nav, col_main = st.columns([1, 3])
    
    with col_nav:
        new_ticker = st.text_input("新增代碼 (如 AMD)", "").upper()
        if st.button("➕ 加入") and new_ticker:
            if new_ticker not in st.session_state['watchlist']:
                st.session_state['watchlist'].append(new_ticker)
        
        selected_watch = st.radio("我的清單", st.session_state['watchlist'])
    
    with col_main:
        if selected_watch:
            # 即時抓取單一股票數據進行分析
            df_watch = yf.download(selected_watch, period="1y", progress=False)
            if not df_watch.empty:
                # 嘗試分析是否有 Setup
                res = analyze_stock_logic(selected_watch, df_watch)
                
                if res:
                    # 如果有 Setup，顯示完整分析
                    display_full_analysis(res)
                else:
                    # 如果沒有 Setup，顯示基本報價 + 圖表 (不顯示 Entry/Stop)
                    curr = df_watch['Close'].iloc[-1]
                    st.markdown(f"### {selected_watch} - 暫無特定型態")
                    st.metric("現價", f"${curr:.2f}")
                    # TradingView
                    tv_html = f"""
                    <div class="tradingview-widget-container" style="height:500px;width:100%">
                      <div id="tv_{selected_watch}" style="height:100%"></div>
                      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                      <script type="text/javascript">
                      new TradingView.widget({{ "autosize": true, "symbol": "{selected_watch}", "interval": "D", "theme": "dark", "style": "1", "container_id": "tv_{selected_watch}" }});
                      </script>
                    </div>
                    """
                    components.html(tv_html, height=510)

# --- 模式 3: TSLA 戰情室 (保留 v3 的修復) ---
elif mode == "⚡ TSLA 戰情室 (Intel)":
    st.markdown("<h2 style='text-align:center; color:white; text-shadow:0 0 10px #000;'>⚡ TESLA WAR ROOM</h2>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.link_button("🌐 Google News", "https://www.google.com/search?q=Tesla+stock&tbm=nws", use_container_width=True)
    c2.link_button("🐦 X (Elon Musk)", "https://twitter.com/elonmusk", use_container_width=True)
    c3.link_button("📈 TradingView", "https://www.tradingview.com/chart/?symbol=TSLA", use_container_width=True)
    
    st.divider()
    
    col_l, col_r = st.columns([1, 2])
    with col_l:
        st.markdown("### 📊 TSLA Live")
        try:
            t = yf.Ticker("TSLA")
            hist = t.history(period="1d")
            if not hist.empty:
                curr = hist['Close'].iloc[-1]
                chg = curr - hist['Open'].iloc[0]
                color = "green" if chg >= 0 else "red"
                st.markdown(f"<h1 style='color:{color};'>${curr:.2f}</h1>", unsafe_allow_html=True)
        except: st.error("No Data")
        
        # 迷你圖
        components.html("""
        <div class="tradingview-widget-container">
          <div class="tradingview-widget-container__widget"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
          { "symbol": "NASDAQ:TSLA", "width": "100%", "height": "300", "dateRange": "12M", "colorTheme": "dark", "isTransparent": true, "autosize": false, "largeChartUrl": "" }
          </script>
        </div>
        """, height=310)
        
    with col_r:
        st.markdown("### 💬 Community Pulse")
        msgs = get_stocktwits("TSLA")
        if msgs:
            for m in msgs[:6]:
                body = m.get('body')
                user = m.get('user', {}).get('username')
                st.markdown(f"<div class='twit-card'><b>@{user}</b><br>{body}</div>", unsafe_allow_html=True)
        else:
            st.warning("社群數據連線中...")
